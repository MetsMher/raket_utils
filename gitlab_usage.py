# ! /usr/local/python/3.12.1/bin/python3

import gitlab
import time
import getpass
import logging
import sys
import os
import gitlab.exceptions
from pathlib import Path


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    # filename="gitlab_log.log",
                    # filemode="a",
                    stream=sys.stdout,
                    level=logging.INFO,
                    )


class GitlabUtil:
    def __init__(self, name, language):
        self.token = os.getenv("GITLAB_TOKEN") or getpass.getpass("🔑 Введите GitLab токен: ")
        self.name = name
        self.user = None
        self.project_id = None
        self.language = language
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        for i in range(3):
            try:
                self.gl = gitlab.Gitlab(private_token=self.token)
                self.gl.auth()
                self.user = self.gl.user
                logging.info(f"Пользователь: {self.user.username:}[{self.user.id}] успешно авторизовался!")
                break
            except gitlab.exceptions.GitlabAuthenticationError as e:
                logging.warning(f'Не найдена переменная GITLAB_TOKEN для авторизации')
                if i < 3:
                    logging.warning(f"У вас {3 - i} попытки")
                    self.token = getpass.getpass("🔑 Введите GitLab токен: ")
            except gitlab.exceptions.GitlabHttpError as e:
                logging.error(f"HTTP статус: {e}")
                exit(1)
            except gitlab.exceptions.GitlabGetError as e:
                logging.error(f"Ошибка аутентификации HTTP статус: {e}")
                exit(1)
        else:
            logging.error("Превышено максимальное количество попыток ввода токена.")
            exit(1)

    def create(self):
        try:
            projects = self.gl.projects.list(search=self.name, owned=True)
            if not projects:
                project = self.gl.projects.create({
                    'name': self.name,
                    'visibility': 'private'
                })
                self.project_id = project.get_id()  # Stanum enq project ID u pahum enq self project_id- um
                logging.info(f'User: {self.user.username} create Project "{self.name}"')
                return
            else:
                logging.info(f'Project "{self.name}" has already been created.')
                exit(1)
        except Exception as e:
            logging.error(f'[ERROR]: {e}')

    def add_base_files_for_project(self):

        # def file_generate(
        #         file_path: str,
        #         content,
        #         author_email,
        #         author_name
        # ):
        #     data = {
        #         'file_path': file_path,
        #         'branch': 'main',
        #         'content': content,
        #         'author_email': author_email,
        #         'author_name': author_name
        #     }
        #     return data
        # # Добавляет файлы по отдельно по одному commit
        # files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        # project = self.gl.projects.get(self.project_id, lazy=True)
        # for file in files:
        #     file_path = Path(f'./temps_files/{self.language}/{file}').read_text()
        #     project.files.create(
        #         file_generate(file_path=file,
        #                       content=file_path,
        #                       author_name=self.user.username,
        #                       author_email=self.user.email)
        #     )
        #     logging.info(f'file {file} has already been created.')

        files = ( ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        project = self.gl.projects.get(self.project_id, lazy=True)

        # Собираем все файлы для одного коммита
        commit_data = {
            'branch': 'main',
            'commit_message': 'Initial project setup with all configuration files',
            'actions': []
        }

        for file in files:
            file_path = Path(f'./temps_files/{self.language}/{file}').read_text()
            commit_data['actions'].append({
                'action': 'create',
                'file_path': file,
                'content': file_path,
                'author_email': self.user.email,
                'author_name': self.user.username
            })
            logging.info(f'Added {file} for commit')

        # Создаем один коммит со всеми файлами
        project.commits.create(commit_data)
        logging.info('All files committed in a single commit')

    def add_branches(self):
        project = self.gl.projects.get(self.project_id, lazy=False)
        try:
            project.branches.create({'branch': 'develop',
                                     'ref': 'main'})
        except Exception as e:
            logging.info(f'{e}')

    def protected_branches(self):
        project = self.gl.projects.get(self.project_id, lazy=False)
        branch_name = 'main'
        protect_branch = project.protectedbranches.get(branch_name)
        protect_branch.delete()

        try:
            project.protectedbranches.create({
                    'name': branch_name,
                    'push_access_level': gitlab.const.AccessLevel.NO_ACCESS,
                    'merge_access_level': gitlab.const.AccessLevel.DEVELOPER,
                })
            logging.info(f'Protected branch "{branch_name}" created.')
        except gitlab.exceptions.GitlabCreateError as e:
            logging.warning(f'Failed to create protected branch: {e}')

        project.protectedbranches.create(
            {
                'name': 'develop',
                'push_access_level': gitlab.const.AccessLevel.DEVELOPER,  # Push разрешён для разработчиков
                'merge_access_level': gitlab.const.AccessLevel.DEVELOPER,  # Merge разрешён для разработчиков
                'unprotect_access_level': gitlab.const.AccessLevel.MAINTAINER,  # Снять защиту могут только мейнтейнеры
                'code_owner_approval_required': False,  # Требовать approval от CODEOWNERS (опционально)
                'allowed_to_push': [{'access_level': gitlab.const.AccessLevel.DEVELOPER}],
                'allowed_to_merge': [{'access_level': gitlab.const.AccessLevel.DEVELOPER}],
        })
        logging.info(f'Protected branch "develop" created:')


    def delete(self):
        projects_name = self.gl.projects.list(search=self.name, owned=True)
        if projects_name:
            self.gl.projects.delete(projects_name[0].id)
            logging.info(f'User: {self.user.username} Deleted "{self.name}" Project')
        else:
            logging.info(f"Project '{self.name}' Does Not Exist!")


if __name__ == "__main__":
    inst = GitlabUtil("Test", 'python')
    time.sleep(0.5)
    inst.create()
    inst.add_base_files_for_project()
    inst.add_branches()
    inst.protected_branches()
    time.sleep(1)
    # inst.delete()
    logging.info("Процесс завершен успешно")
