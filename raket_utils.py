import gitlab
import time
import getpass
import logging
import gitlab.exceptions
from pathlib import Path
from typing import Optional
import typer
import os
import sys
from rich.logging import RichHandler

def get_path(relative_path):
    """Получает абсолютный путь к файлу, учитывая временную папку PyInstaller."""
    if hasattr(sys, '_MEIPASS'):  # Если запущено из собранного бинарника
        base_path = sys._MEIPASS
    else:  # Если запущено из исходного кода
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Настройка логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Обработчик для вывода в консоль с использованием rich
console_handler = RichHandler(markup=True)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

# Обработчик для записи в файл без rich
file_handler = logging.FileHandler(filename='log.txt', mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


class GitlabUtil:
    def __init__(self, name, language=None):
        self.token = os.getenv("GITLAB_TOKEN")
        if not self.token:
            logger.info("GITLAB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
            self.token = getpass.getpass("🔑 Введите GITLAB ACCESS TOKEN: ")
        self.name = name
        self.gl = None
        self.user = None
        self.project_id = None
        self.language = language
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        

    def auth(self):
        for i in range(2):
            try:
                self.gl = gitlab.Gitlab(private_token=self.token)
                self.gl.auth()
                self.user = self.gl.user
                logger.info(f"Пользователь: {self.user.username:}[{self.user.id}] успешно авторизовался! :🤑:")
                break
            except gitlab.exceptions.GitlabAuthenticationError as e:
                if i < 2:
                    logger.warning(f'Ошибка при авторизации {e}: У вас {2 - i} попытки')
                    self.token = getpass.getpass("🔑 Введите GitLab токен: ")
            except gitlab.exceptions.GitlabHttpError as e:
                logger.error(f"HTTP статус: {e}")
                exit(1)
            except gitlab.exceptions.GitlabGetError as e:
                logger.error(f"Ошибка аутентификации HTTP статус: {e}")
                exit(1)
        else:
            logger.error("Превышено максимальное количество попыток ввода токена.")
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
                logger.info(f'User: {self.user.username} create Project "{self.name}"')
                return
            else:
                logger.info(f'Project "{self.name}" has already been created.')
                sys.exit()
        except Exception as e:
            logger.error(f'[ERROR]: {e}')


    def add_base_files_for_project(self):
        # Получаем путь через модуль pathlib который не подходит для использования через build проекта

        # files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        # project = self.gl.projects.get(self.project_id, lazy=True)
        #
        # # Собираем все файлы для одного коммита
        # commit_data = {
        #     'branch': 'main',
        #     'commit_message': 'Initial project setup with all configuration files',
        #     'actions': []
        # }
        #
        # for file in files:
        #     file_path = Path(f'./temps_files/{self.language}/{file}').read_text()
        #     commit_data['actions'].append({
        #         'action': 'create',
        #         'file_path': file,
        #         'content': file_path,
        #         'author_email': self.user.email,
        #         'author_name': self.user.username
        #     })
        #     logging.info(f'Added {file} for commit')
        #
        # # Создаем один коммит со всеми файлами
        # project.commits.create(commit_data)
        # logging.info('All files committed in a single commit')

        files = ("README.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
        project = self.gl.projects.get(self.project_id, lazy=True)

        # Собираем все файлы для одного коммита
        commit_data = {
            'branch': 'main',
            'commit_message': 'Initial project setup with all configuration files',
            'actions': []
        }

        for file in files:
            try:
                # Используем get_path для получения правильного пути
                file_path = get_path(f'temps_files/{self.language}/{file}')
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                commit_data['actions'].append({
                    'action': 'create',
                    'file_path': file,
                    'content': content,
                    'author_email': self.user.email,
                    'author_name': self.user.username
                })
                logger.info(f'Added {file} for commit')
            except FileNotFoundError as e:
                logger.error(f'File not found: {file_path}')
                raise

        # Создаем один коммит со всеми файлами
        project.commits.create(commit_data)
        logger.info('All files committed in a single commit')


    def add_branches(self):
        project = self.gl.projects.get(self.project_id, lazy=False)
        try:
            project.branches.create({'branch': 'develop',
                                     'ref': 'main'})
        except Exception as e:
            logger.info(f'{e}')


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
            logger.info(f'Protected branch "{branch_name}" created.')
        except gitlab.exceptions.GitlabCreateError as e:
            logger.warning(f'Failed to create protected branch: {e}')

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
        logger.info(f'Protected branch "develop" created:')


    def delete(self):
        projects_name = self.gl.projects.list(search=self.name, owned=True)
        if projects_name:
            self.gl.projects.delete(projects_name[0].id)
            logger.info(f'User: {self.user.username} Deleted "{self.name}" Project')
        else:
            logger.info(f"Project '{self.name}' Does Not Exist!")


def create_project(name, lang: Optional[str]):
    inst = GitlabUtil(name, lang)
    inst.auth()
    time.sleep(0.5)
    inst.create()
    inst.add_base_files_for_project()
    inst.add_branches()
    inst.protected_branches()
    time.sleep(1)
    logger.info("Процесс завершен успешно")


def delete_project(name: str):
    inst = GitlabUtil(name)
    inst.auth()
    inst.delete()


app = typer.Typer(add_completion=False)


@app.command()
def create(
           lang: str = typer.Option(..., "--lang", "-l", help="Language of the project.", show_default=False),
           name: str = typer.Option(..., "--name", "-n", help="Name of the project.", show_default=False)):
    
    """
    Команда для создания нового проекта.
    
    Аргументы:
    name: Имя проекта
    lang: Язык проекта
    """
    create_project(name, lang)



@app.command()
def delete(name: str = typer.Option(..., "--name", "-n", help="Name of the project.", show_default=False)):

    """
    Команда для удаления проекта.

    Аргумент:
    name: Имя проекта (--name, -n)
    """

    delete_project(name)


if __name__ == "__main__":
    app()
