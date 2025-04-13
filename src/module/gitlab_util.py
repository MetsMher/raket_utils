# from contextlib import contextmanager
#
# from gitlab import exceptions
# from gitlab import const
# from gitlab import Gitlab
#
# import getpass
#
# import os
#
# import sys
#
# from logger import logger
#
# from pathlib import Path
#
#
# # def get_path(relative_path):
# #     """Получает абсолютный путь к файлу, учитывая временную папку PyInstaller."""
# #     if hasattr(sys, '_MEIPASS'):  # Если запущено из собранного бинарника
# #         base_path = sys._MEIPASS
# #     else:  # Если запущено из исходного кода
# #         base_path = os.path.abspath("./src/")
# #     return os.path.join(base_path, relative_path)
#
# class GitlabUtil:
#     def __init__(self, name, language=None):
#         self.token = os.getenv("GITLAB_TOKEN")
#         if not self.token:
#             logger.info("GITLAB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
#             self.token = getpass.getpass("🔑 Введите GITLAB ACCESS TOKEN: ")
#         self.name = name
#         self.gl = None
#         self.user = None
#         self.__project_id = None
#         self.language = language
#         self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
#
#
#     def auth(self):
#         for i in range(3):
#             print(i)
#             try:
#                 self.gl = Gitlab(private_token=self.token)
#                 self.gl.auth()
#                 self.user = self.gl.user
#                 logger.info(f"Пользователь: {self.user.username:}[{self.user.id}] успешно авторизовался! 🤑")
#                 break
#             except exceptions.GitlabAuthenticationError as e:
#                 if i < 2:
#                     logger.warning(f'Ошибка при авторизации {e}: У вас {2 - i} попытки')
#                     self.token = getpass.getpass("🔑 Введите GitLab токен: ")
#             except exceptions.GitlabHttpError as e:
#                 logger.error(f"HTTP статус: {e}")
#                 exit(1)
#             except exceptions.GitlabGetError as e:
#                 logger.error(f"Ошибка аутентификации HTTP статус: {e}")
#                 exit(1)
#         else:
#             logger.error("Превышено максимальное количество попыток ввода токена.")
#             exit(1)
#
#     @contextmanager
#     def managed_project(self):
#         """Контекстный менеджер для автоматического rollback при ошибках."""
#         try:
#             # self._create_project()  # Создаём проект
#             yield self  # Возвращаем управление в блок `with`
#         except Exception as e:
#             logger.error(f"Ошибка: {e}. Выполняем rollback...")
#             self.delete_project()  # Удаляем проект при ошибке
#             raise  # Пробрасываем исключение дальше
#         # Если ошибок не было, проект остаётся
#
#
#     def create_project(self):
#         try:
#             projects = self.gl.projects.list(search=self.name, owned=True)
#             if not projects:
#                 project = self.gl.projects.create({
#                     'name': self.name,
#                     'visibility': 'private'
#                 })
#                 self.__project_id = project.get_id()  # Stanum enq project ID u pahum enq self project_id um
#                 logger.info(f'User: {self.user.username} create Project "{self.name}"')
#                 return
#             else:
#                 logger.info(f'Project "{self.name}" has already been created.')
#                 exit(1)
#         except Exception as e:
#             logger.error(f'[ERROR]: {e}')
#             raise
#
#     def add_base_files_for_project(self):
#         files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
#         project = self.gl.projects.get(self.__project_id, lazy=True)
#
#         # Собираем все файлы для одного коммита
#         commit_data = {
#             'branch': 'main',
#             'commit_message': 'Initial project setup with all configuration files',
#             'actions': []
#         }
#
#         for file in files:
#             try:
#                 # Используем get_path для получения правильного пути
#                 # file_path = get_path(f'./data/temps_files/{self.language}/{file}')
#                 # with open(file_path, 'r', encoding='utf-8') as f:
#                 #     content = f.read()
#
#                 content = Path(f'./src/data/temps_files/{self.language}/{file}').read_text(encoding='utf-8')
#
#                 commit_data['actions'].append({
#                     'action': 'create',
#                     'file_path': file,
#                     'content': content,
#                     'author_email': self.user.email,
#                     'author_name': self.user.username
#                 })
#                 logger.info(f'Added {file} for commit')
#             except:
#                 # logger.error(f'File not found: {e}')
#                 raise
#
#         # Создаем один коммит со всеми файлами
#         project.commits.create(commit_data)
#         logger.info('All files committed in a single commit')
#
#
#     def add_branches_project(self):
#         project = self.gl.projects.get(self.__project_id, lazy=False)
#         try:
#             project.branches.create({'branch': 'develop',
#                                      'ref': 'main'})
#         except Exception as e:
#             logger.info(f'{e}')
#             raise
#
#     def protected_branches_project(self):
#         project = self.gl.projects.get(self.__project_id, lazy=False)
#         branch_name = 'main'
#         protect_branch = project.protectedbranches.get(branch_name)
#         protect_branch.delete()
#
#         try:
#             project.protectedbranches.create({
#                     'name': branch_name,
#                     'push_access_level': const.AccessLevel.NO_ACCESS,
#                     'merge_access_level': const.AccessLevel.DEVELOPER,
#                 })
#             logger.info(f'Protected branch "{branch_name}" created.')
#         except exceptions.GitlabCreateError as e:
#             logger.error(f'Failed to create protected branch: {e}')
#             raise
#
#         try:
#             project.protectedbranches.create(
#                 {
#                     'name': 'develop',
#                     'push_access_level': const.AccessLevel.DEVELOPER,  # Push разрешён для разработчиков
#                     'merge_access_level': const.AccessLevel.DEVELOPER,  # Merge разрешён для разработчиков
#                     'unprotect_access_level': const.AccessLevel.MAINTAINER,  # Снять защиту могут только мейнтейнеры
#                     'code_owner_approval_required': False,  # Требовать approval от CODEOWNERS (опционально)
#                     'allowed_to_push': [{'access_level': const.AccessLevel.DEVELOPER}],
#                     'allowed_to_merge': [{'access_level': const.AccessLevel.DEVELOPER}],
#             })
#             logger.info(f'Protected branch "develop" created:')
#         except Exception as e:
#             logger.error(f'{e}')
#             raise
#
#
#     def delete_project(self):
#         projects_name = self.gl.projects.list(search=self.name, owned=True)
#         if projects_name:
#             self.gl.projects.delete(projects_name[0].id)
#             logger.info(f'User: {self.user.username} Deleted "{self.name}" Project')
#         else:
#             logger.info(f"Project '{self.name}' Does Not Exist!")
#
#
# if __name__ == "__main__":
#     try:
#         util = GitlabUtil(name="test-projj11111", language="Python1")
#         util.auth()
#         util.create_project()
#         try:
#             with util.managed_project():  # Проект создаётся здесь
#                 util.add_base_files_for_project()  # Добавляем файлы
#                 util.add_branches_project()                # Создаём ветки
#                 util.protected_branches_project()         # Защищаем ветки
#                 # Если здесь упадёт ошибка - проект удалится автоматически!
#             logger.info("✅ Всё успешно завершено! Проект создан.")
#         except:
#             logger.error(f":boom: Проект удалён (rollback).")
#             exit(1)
#     except Exception as e:
#         logger.error(f"❌ Ошибка: {e}")
#         exit(1)


from contextlib import contextmanager
from gitlab import exceptions, const, Gitlab
import getpass
import os
# import traceback
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
            logger.error(f"Ошибка: {e}\nВыполняем rollback...")
            for action in reversed(self.rollback_actions):
                try:
                    action()
                except Exception as rollback_error:
                    logger.warning(f"Ошибка rollback-действия: {rollback_error}")
            raise

    def create_project(self):
        try:
            projects = self.gl.projects.list(search=self.name, owned=True)
            if not projects:
                project = self.gl.projects.create({
                    'name': self.name,
                    'visibility': 'private'
                })
                self.__project_id = project.id
                self.project_created = True
                self.rollback_actions.append(lambda: self.delete_project(silent=True))
                logger.info(f'Проект "{self.name}" успешно создан.')
            else:
                raise RuntimeError(f'Проект "{self.name}" уже существует.')
        except Exception as e:
            logger.error(f'Ошибка при создании проекта: {e}')
            raise

    def add_base_files_for_project(self):
        files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        project = self.gl.projects.get(self.__project_id, lazy=True)
        commit_data = {
            'branch': 'main',
            'commit_message': 'Initial project setup with all configuration files',
            'actions': []
        }

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
        try:
            project.branches.create({'branch': 'develop', 'ref': 'main'})
            logger.info('Ветка "develop" успешно создана.')
        except Exception as e:
            logger.error(f'Ошибка при создании ветки "develop": {e}')
            raise

    def protected_branches_project(self):
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
            projects_name = self.gl.projects.list(search=self.name, owned=True)
            if projects_name or self.project_created:
                self.gl.projects.delete(projects_name[0].id)
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