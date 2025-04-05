# #! /usr/local/python/3.12.1/bin/python3
#
# import gitlab
# import time
# import getpass
# import logging
# import sys
# import os
# import gitlab.exceptions
#
# content = """
# stages:
#   - test
#
# test-utils:
#   stage: test
#   script:
#     - >
#       echo "This is good utils!:) "
# """
#
# logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
#                     datefmt="%Y-%m-%d %H:%M:%S",
#                     # filename="gitlab_log.log",
#                     # filemode="a",
#                     stream=sys.stdout,
#                     level=logging.INFO,
#                     )
#
#
# class GitlabUtil:
#     def __init__(self, name):
#         self.token = os.getenv("GITLAB_TOKEN") or getpass.getpass("🔑 Введите GitLab токен: ")
#         self.name = name
#         self.user = None
#         self.project_id = None
#         self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
#         for i in range(2):
#             try:
#                 self.gl = gitlab.Gitlab(private_token=self.token)
#                 self.gl.auth()
#                 self.user = self.gl.user
#                 logging.info(f"Пользователь: {self.user.username:}[{self.user.id}] успешно авторизовался!")
#                 break
#             except gitlab.exceptions.GitlabAuthenticationError as e:
#                 logging.error(f'Ошибка аутентификации {e}')
#                 if i < 3 - 1:
#                     logging.warning(f"У вас осталось {3 - i - 1} попытка(ок)")
#                     token = getpass.getpass("🔑 Введите GitLab токен: ")
#             except gitlab.exceptions.GitlabHttpError as e:
#                 logging.error(f"HTTP статус: {e}")
#                 exit(1)
#             except gitlab.exceptions.GitlabGetError as e:
#                 logging.error(f"Ошибка аутентификации HTTP статус: {e}")
#                 exit(1)
#         else:
#             logging.error("Превышено максимальное количество попыток ввода токена.")
#             exit(1)
#
#     def create(self):
#         try:
#             projects = self.gl.projects.list(search=self.name, owned=True)
#             if not projects:
#                 self.gl.projects.create({'name': self.name})
#                 logging.info(f'User: {self.user.username} create Project "{self.name}"')
#                 return
#             else:
#                 # self.project_id = projects[0].id
#                 logging.info(f'Project "{self.name}" has already been created.')
#                 # exit(1)
#         except Exception as e:
#             logging.error(f'[ERROR]: {e}')
#             exit(1)
#
#     def add_base_files_for_project(self):
#         # projects = self.gl.projects.list(search=self.name, owned=True)
#         # if not projects:
#         #     logging.error(f'Проект с именем {self.name} не найден!')
#         #     return
#         # project = projects[0]
#         # self.project_id = project.id
#         # # Определяем путь к файлу и его содержимое
#         # file_path = '.gitlab-ci.yml'
#         #
#         # try:
#         #     project.files.create({
#         #         'file_path': file_path,
#         #         'branch': 'main',
#         #         'content': content,
#         #         'commit_message': f'Создан файл {file_path}',
#         #         'author_name': self.user.username,
#         #         'author_email': self.user.email
#         #     })
#         #     logging.info(f'Файл {file_path} успешно создан в проекте.')
#         # except Exception as e:
#         #     logging.error(f'{e}')
#         project = self.gl.projects.get(self.project_id, lazy=False)
#         project.files.create({
#             'file_path': '.gitlab-ci.yml',
#             'branch': 'main',
#             'content': content,
#             'author_email': 'mher07@icloud.com',
#             'author_name': 'MetsMher',
#             'commit_message': 'Create testfile'
#         })
#         logging.info(f'file created.')
#
#     def add_branches(self):
#         project = self.gl.projects.get(self.project_id, lazy=False)
#         try:
#             project.branches.create({'branch': 'develop',
#                                      'ref': 'main'})
#         except Exception as e:
#             logging.info(f'{e}')
#
#     def protected_branches(self):
#         project = self.gl.projects.get(self.project_id, lazy=False)
#         try:
#             project.protectedbranches.create({
#                 'name': 'main',
#                 'merge_access_level': project.gitlab.const.AccessLevel.DEVELOPER,  # Мёрж через MR (но не напрямую!)
#                 'push_access_level': project.gitlab.const.AccessLevel.NO_ACCESS,  # Прямой пуш запрещён
#             })
#         except gitlab.exceptions.GitlabCreateError as e:
#             logging.error(f'{e}')
#
#
#     def delete(self):
#         projects_name = self.gl.projects.list(search=self.name, owned=True)
#         if projects_name:
#             self.gl.projects.delete(projects_name[0].id)
#             logging.info(f'User: {self.user.username} Deleted "{self.name}" Project')
#         else:
#             logging.info(f"Project '{self.name}' Does Not Exist!")
#
#     # This is Commit Taron Ghazaryan
#     # def delete(self):
#     #     if self.name is not None:
#     #         project_id = self.gl.projects.list(search=self.name, owned=True)[0].id
#     #         self.gl.projects.delete(project_id)
#     #         logging.info(f'User: {self.user.username} Deleted "{self.name}" Project')
#     #     else:
#     #         logging.info(f"Project '{self.name}' Does Not Exist!")
#
#
# if __name__ == "__main__":
#     inst = GitlabUtil("Test111")
#     time.sleep(0.5)
#     inst.create()
#     inst.add_base_files_for_project()
#     inst.add_branches()
#     inst.protected_branches()
#     time.sleep(1)
#     inst.delete()



#! /usr/local/python/3.12.1/bin/python3

import gitlab
import time
import getpass
import logging
import sys
import os
import json
import gitlab.exceptions
from pathlib import Path


from pathlib import Path

content = """
stages:
  - test

test-utils:
  image: alpine
  stage: test
  script:
    - >
      echo "This is good utils!:) "
"""


def choice_gi(language: str):
    with open('./gitignore.json', 'r') as f:
        git_dict = json.load(f)
    gitignore_file = Path(f"{git_dict[language]}").read_text(encoding="utf-8")
    return gitignore_file



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
        for i in range(2):
            try:
                self.gl = gitlab.Gitlab(private_token=self.token)
                self.gl.auth()
                self.user = self.gl.user
                logging.info(f"Пользователь: {self.user.username:}[{self.user.id}] успешно авторизовался!")
                break
            except gitlab.exceptions.GitlabAuthenticationError as e:
                logging.error(f'Ошибка аутентификации {e}')
                if i < 3 - 1:
                    logging.warning(f"У вас осталось {3 - i - 1} попытка(ок)")
                    token = getpass.getpass("🔑 Введите GitLab токен: ")
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
                project = self.gl.projects.create({'name': self.name})
                self.project_id = project.get_id()
                project.files.create({
                    'file_path': '.gitignoe',
                    'branch': 'main',
                    'content': choice_gi(self.language),
                    'author_email': 'mher07@icloud.com',
                    'author_name': 'MetsMher',
                    'commit_message': 'Create testfile'
                })
                logging.info(f'file  has already been created.')
                logging.info(f'User: {self.user.username} create Project "{self.name}"')
                return
            else:
                logging.info(f'Project "{self.name}" has already been created.')
                exit(1)
        except Exception as e:
            logging.error(f'[ERROR]: {e}')

    def add_base_files_for_project(self):
        # projects = self.gl.projects.list(search=self.name, owned=True)
        # if not projects:
        #     logging.error(f'Проект с именем {self.name} не найден!')
        #     return
        # project = projects[0]
        # self.project_id = project.id
        # # Определяем путь к файлу и его содержимое
        # file_path = '.gitlab-ci.yml'
        #
        # try:
        #     project.files.create({
        #         'file_path': file_path,
        #         'branch': 'main',
        #         'content': content,
        #         'commit_message': f'Создан файл {file_path}',
        #         'author_name': self.user.username,
        #         'author_email': self.user.email
        #     })
        #     logging.info(f'Файл {file_path} успешно создан в проекте.')
        # except Exception as e:
        #     logging.error(f'{e}')

        project = self.gl.projects.get(self.project_id, lazy=True)
        project.files.create({
            'file_path': '.gitlab-ci.yml',
            'branch': 'main',
            'content': content,
            'author_email': 'mher07@icloud.com',
            'author_name': 'MetsMher',
            'commit_message': 'Create testfile'
        })
        logging.info(f'file  has already been created.')



    def add_branches(self):
        project = self.gl.projects.get(self.project_id, lazy=False)
        try:
            project.branches.create({'branch': 'develop',
                                     'ref': 'main'})
        except Exception as e:
            logging.info(f'{e}')

    def protected_branches(self):
        project = self.gl.projects.get(self.project_id, lazy=False)
        try:
            project.protectedbranches.create({
               'name': 'main',
               'merge_access_level': gitlab.const.AccessLevel.DEVELOPER,  # Мёрж через MR (но не напрямую!)
               'push_access_level': gitlab.const.AccessLevel.NO_ACCESS,  # Прямой пуш запрещён
            })
        except gitlab.exceptions.GitlabCreateError as e:
            logging.warning(f'{e}')


    def delete(self):
        projects_name = self.gl.projects.list(search=self.name, owned=True)
        if projects_name:
            self.gl.projects.delete(projects_name[0].id)
            logging.info(f'User: {self.user.username} Deleted "{self.name}" Project')
        else:
            logging.info(f"Project '{self.name}' Does Not Exist!")

    # def delete(self):
    #     if self.name is not None:
    #         project_id = self.gl.projects.list(search=self.name, owned=True)[0].id
    #         self.gl.projects.delete(project_id)
    #         logging.info(f'User: {self.user.username} Deleted "{self.name}" Project')
    #     else:
    #         logging.info(f"Project '{self.name}' Does Not Exist!")


if __name__ == "__main__":
    inst = GitlabUtil("Test1", 'c++')
    time.sleep(0.5)
    inst.create()
    inst.add_base_files_for_project()
    inst.add_branches()
    inst.protected_branches()
    # time.sleep(1)
    # inst.delete()
    logging.info("Процесс завершен успешно")