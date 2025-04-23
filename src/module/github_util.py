from contextlib import contextmanager

from github import Github, Auth, GithubException, InputGitTreeElement

from os import getenv

from pathlib import Path

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
            logger.error(f"Ошибка: {e}\n Выполняем rollback...")
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
            # try:
                repo = self.user.create_repo(
                    name=self.repo_name,
                    description="Test create repo in class GitHubUtil",
                    private=False,
                    # gitignore_template="Go",
                    # auto_init=True,
                    has_issues=True,
                    has_wiki=True,
                    has_downloads=True,
                    has_projects=True,
                    allow_squash_merge=True,
                    allow_merge_commit=True,
                    allow_rebase_merge=True,  
                    delete_branch_on_merge=True,
                    # default_branch="develop",
                )

                self.project_created = True
                logger.info(f'This is your create repo link {repo.html_url}')
        except Exception as create_repo_error:
            # Если не удалось создать репозиторий, логируем ошибку
            # и пробрасываем исключение, чтобы вызвать rollback
            logger.error(f'Ошибка при создании репозитория: {create_repo_error}')
            raise  # Пробрасываем исключение только если не смогли создать


    def create_branches(self):
        self.rollback_actions.append(lambda: self.delete_repo(silent=True))
        try:
            repo = self.user.get_repo(self.repo_name)
            # if not repo:
            #     logger.error(f'Проект "{self.repo_name}" не был создан, ветки создавать нечего.')
            #     return
            # Создаем ветку test
            repo.create_git_ref(ref="refs/heads/develop", sha=repo.get_branch("main").commit.sha)


            # logger.info(f'Ветки develop успешно созданы в проекте {self.repo_name}')
        except Exception as e:
            # logger.error(f'Ошибка при создании веток: {e}')
            raise

    
    # def add_base_files_for_project(self):
    #     repo = self.user.get_repo(self.repo_name)
    #     files = ("README.md", "gitflow-branch-rules.md", ".dockerignore", ".gitignore", ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml")
    #     self.rollback_actions.append(lambda: self.delete_repo(silent=True))
    #     try:
    #         for file in files:
    #             content = Path(f'./src/data/temps_files/{self.language}/{file}').read_text(encoding='utf-8')
    #             repo.create_file(file, f"Добавлен файл {file}", content, branch="main")
    #     except Exception as e:
    #         logger.error(f'Ошибка при добавлении файла: {e}')
    #         raise


    def add_base_files_for_project(self):
        repo = self.user.get_repo(self.repo_name)
        self.rollback_actions.append(lambda: self.delete_repo(silent=True))
        
        files = (
            "README.md", "gitflow-branch-rules.md", ".dockerignore", ".gitignore",
            ".gitlab-ci.yml", "Dockerfile", "docker-compose.yml"
        )

        try:
            # Получаем SHA последнего коммита в main
            main_ref = repo.get_git_ref('heads/main')
            base_commit = repo.get_git_commit(main_ref.object.sha)
            base_tree = base_commit.tree

            # Создаём список элементов дерева
            tree_elements = []
            for file in files:
                file_path = f'./src/data/temps_files/{self.language}/{file}'
                content = Path(file_path).read_text(encoding='utf-8')
                blob = repo.create_git_blob(content, "utf-8")
                element = InputGitTreeElement(path=file, mode='100644', type='blob', sha=blob.sha)
                tree_elements.append(element)

            # Создаём новое дерево и коммит
            new_tree = repo.create_git_tree(tree=tree_elements, base_tree=base_tree)
            commit_message = "Добавлены базовые файлы проекта"
            new_commit = repo.create_git_commit(commit_message, new_tree, [base_commit])
            
            # Обновляем ссылку main на новый коммит
            main_ref.edit(new_commit.sha)
            
        except Exception as e:
            logger.error(f'Ошибка при добавлении файлов: {e}')
            raise


    def delete_repo(self, silent=False):
        try:
            repo = self.user.get_repo(self.repo_name)
            if repo:
                repo.delete()
                logger.info(f"Проект {self.repo_name} удален")
            elif not silent:
                logger.error(f'Проект "{self.repo_name}" не был создан, удалять нечего.')
        except Exception as e:
            if not silent:
                logger.error(f'Ошибка при удалении проекта: {e}')


    def repo_list(self):
        repos = self.user.get_repos()
        for repo in repos:
            print(f'Repository: {repo.full_name} - Language: {repo.language}')