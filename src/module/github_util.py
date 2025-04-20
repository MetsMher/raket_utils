from contextlib import contextmanager

from github import Github, Auth, GithubException

from os import getenv

from getpass import getpass

from logger import logger

class GitHubUtil:
    def __init__(self, repo_name, language=None):
        self.token = getenv("GITHUB_TOKEN")
        if not self.token:
            print("Переменная GITHUB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
            self.token = getpass("🔑 Введите GITHUB ACCESS TOKEN: ")
        self.repo_name = repo_name
        self.language = language
        self.user = None
        self.project_created = False  # Флаг успешного создания проекта
        self.rollback_actions = []  # Стек rollback-действий

    def auth(self):

        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                auth = Auth.Token(self.token)
                g = Github(auth=auth)
                self.user = g.get_user()
                logger.info(f'Пользователь: {self.user.login}:{self.user.id} успешно авторизовался! 🤑"')
                break
            except GithubException as e:
                logger.error(f'HTTP status {e.status}: У вас осталось {max_attempts - attempt - 1} попыток.')
                if attempt + 1 < max_attempts:
                    self.token = getpass("🔑 Введите GITHUB ACCESS TOKEN: ")
        else:
            logger.error("Превышено максимальное количество попыток ввода токена.")
            exit(1)


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


    def create_repo(self):
        try:
            # Проверяем, существует ли репозиторий
            self.user.get_repo(self.repo_name)
            logger.error(f'Проект "{self.repo_name}" уже существует.')
            exit(1)  # Просто выходим, не вызывая исключение
        except Exception as get_repo_error:
            # Если репозитория нет (get_repo вызвал исключение), пробуем создать
            try:
                repo = self.user.create_repo(
                    name=self.repo_name,
                    description="Test create repo in class GitHubUtil",
                    private=False,
                    gitignore_template="Go",
                    auto_init=True
                )
                self.project_created = True
                logger.info(f'This is your create repo link {repo.html_url}')
            except Exception as create_repo_error:
                logger.error(f'Ошибка при создании репозитория: {create_repo_error}')
                raise  # Пробрасываем исключение только если не смогли создать


    # def create_repo(self):
    #     try:
    #         try:
    #             self.user.get_repo(self.repo_name)
    #             logger.error(f'Проект "{self.repo_name}" уже существует.')
    #
    #             return
    #         except:
    #             repo = self.user.create_repo(
    #                 name=self.repo_name,
    #                 description="Test create repo in class GitHubUtil",
    #                 private=False,
    #                 gitignore_template="Go",
    #                 auto_init=True
    #             )
    #             self.project_created = True
    #             logger.info(f'This is your create repo link {repo.html_url}')
    #     except Exception as e:
    #         logger.error(f'{e}')



    def delete_repo(self, silent=False):
        try:
            repo = self.user.get_repo(self.repo_name)
            if repo:
                repo.delete()
                logger.error(f"Проект {self.repo_name} удален")
        except Exception:
            if not silent:
                logger.error(f'Проект "{self.repo_name}" не был создан, удалять нечего.')
            # logger.info(f'ERROR {e}')
            # if not silent:
            #     logger.error(f'Ошибка при удалении проекта: {e}')


    def repo_list(self):
        repos = self.user.get_repos()
        for repo in repos:
            print(f'Repository: {repo.full_name} - Language: {repo.language}')

# self.rollback_actions.append(lambda: self.delete_project(silent=True))


if __name__ == "__main__":
    init = GitHubUtil("Mher")
    init.auth()
    init.create_repo()
    # init.repo_list()
    # init.delete_repo()
