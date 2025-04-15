from contextlib import contextmanager

from gitlab import exceptions, const, Gitlab

import getpass

import os


from logger import logger

from pathlib import Path


class GitlabUtil:
    def __init__(self, name, language=None):
        self.token = os.getenv("GITLAB_TOKEN")
        if not self.token:
            logger.info("GITLAB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
            self.token = getpass.getpass("🔑 Введите GITLAB ACCESS TOKEN: ")
        self.name = name
        self.language = language
        self.gl = None
        self.user = None
        self.__project_id = None
        self.project_created = False  # Флаг успешного создания проекта
        self.rollback_actions = []  # Стек rollback-действий
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')


    def auth(self):
        for i in range(3):
            try:
                self.gl = Gitlab(self.gitlab_url, private_token=self.token)
                self.gl.auth()
                self.user = self.gl.user
                logger.info(f"Пользователь: {self.user.username}[{self.user.id}] успешно авторизовался!")
                return
            except exceptions.GitlabAuthenticationError as e:
                if i < 2:
                    logger.warning(f'Ошибка авторизации: {e}. Осталось {2 - i} попытки.')
                    self.token = getpass.getpass("🔑 Введите GitLab токен: ")
            except (exceptions.GitlabHttpError, exceptions.GitlabGetError) as e:
                logger.error(f"Ошибка при попытке подключения к GitLab: {e}")
                raise
        raise RuntimeError("Превышено максимальное количество попыток авторизации.")


    @contextmanager
    def managed_project(self):
        try:
            yield self
        except Exception as e:
            logger.error(f"Ошибка: {e} Выполняем rollback...")
            for action in reversed(self.rollback_actions):
                try:
                    action()
                except Exception as rollback_error:
                    logger.warning(f"Ошибка rollback-действия: {rollback_error}")
            raise


    def create_project(self):
        try:
            try:
                self.gl.projects.get(f'{self.user.username}/{self.name}')
                logger.error(f'Проект "{self.name}" уже существует.')
                # exit(1)
                raise
            except:
                project = self.gl.projects.create({
                    'name': self.name,
                    'visibility': 'private',
                    'with_merge_requests_enabled': True,
                    'only_allow_merge_if_pipeline_succeeds': True,
                    'remove_source_branch_after_merge': False,
                    # 'default_branch': 'develop',
                    'wiki_enabled': True,
                    'description': f'Created project for {self.language} language',
                    'container_registry_enabled': True
                })
                self.__project_id = project.id
                self.project_created = True
                logger.info(f'Проект "{self.name}" успешно создан.')
            # else:
                # raise RuntimeError(f'Проект "{self.name}" уже существует.')
        except Exception as e:
            # logger.error(f'Ошибка при создании проекта:')
            raise


    def add_base_files_for_project(self):
        files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        project = self.gl.projects.get(self.__project_id, lazy=True)
        commit_data = {
            'branch': 'main',
            'commit_message': 'Initial project setup with all configuration files',
            'actions': []
        }
        self.rollback_actions.append(lambda: self.delete_project(silent=True))
        for file in files:
            try:
                content = Path(f'./src/data/temps_files/{self.language}/{file}').read_text(encoding='utf-8')
                commit_data['actions'].append({
                    'action': 'create',
                    'file_path': file,
                    'content': content,
                    'author_email': self.user.email,
                    'author_name': self.user.username
                })
                logger.info(f'Файл добавлен для коммита: {file}')
            except FileNotFoundError:
                logger.warning(f'Файл не найден: {file}')
                raise

        project.commits.create(commit_data)
        logger.info('Все файлы закоммичены одним коммитом.')


    def add_branches_project(self):
        project = self.gl.projects.get(self.__project_id)
        self.rollback_actions.append(lambda: self.delete_project(silent=True))
        try:
            project.branches.create({'branch': 'develop', 'ref': 'main'})
            logger.info('Ветка "develop" успешно создана.')
        except Exception as e:
            logger.error(f'Ошибка при создании ветки "develop": {e}')
            raise


    def protected_branches_project(self):
        self.rollback_actions.append(lambda: self.delete_project(silent=True))
        project = self.gl.projects.get(self.__project_id)
        try:
            protect_branch = project.protectedbranches.get('main')
            protect_branch.delete()
        except Exception:
            pass  # Если защита не стоит — окей

        try:
            project.protectedbranches.create({
                'name': 'main',
                'push_access_level': const.AccessLevel.NO_ACCESS,
                'merge_access_level': const.AccessLevel.DEVELOPER,
            })
            logger.info('Ветка "main" защищена.')
        except Exception as e:
            logger.error(f'Ошибка защиты ветки main: {e}')
            raise

        try:
            project.protectedbranches.create({
                'name': 'develop',
                'push_access_level': const.AccessLevel.DEVELOPER,
                'merge_access_level': const.AccessLevel.DEVELOPER,
                'unprotect_access_level': const.AccessLevel.MAINTAINER,
                'code_owner_approval_required': False,
            })
            logger.info('Ветка "develop" защищена.')
        except Exception as e:
            logger.error(f'Ошибка защиты ветки develop: {e}')
            raise


    def delete_project(self, silent=False):
        try:
            project = self.gl.projects.get(f'{self.user.username}/{self.name}')
            if project or self.project_created:
                self.gl.projects.delete(project.id)
                logger.info(f'Проект "{self.name}" удалён.')
            elif not silent:
                logger.info(f'Проект "{self.name}" не был создан, удалять нечего.')
        except Exception as e:
            if not silent:
                logger.error(f'Ошибка при удалении проекта: {e}')


if __name__ == "__main__":
    try:
        util = GitlabUtil(name="testasdsadsadsaadsadp", language="Pytho")
        util.auth()
        util.create_project()
        with util.managed_project():
            util.add_base_files_for_project()
            util.add_branches_project()
            util.protected_branches_project()
        logger.info("✅ Всё успешно завершено! Проект создан.")
    except Exception as e:
        logger.error(f"❌ Ошибка в процессе: {e}")