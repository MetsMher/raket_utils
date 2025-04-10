from github import Github, Auth, GithubException

from os import getenv

from getpass import getpass


class GitHubUtil:
    def __init__(self, repo_name, language=None):
        self.token = getenv("GITHUB_TOKEN")
        if not self.token:
            print("Переменная GITHUB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
            self.token = getpass("🔑 Введите GITHUB ACCESS TOKEN: ")
        self.repo_name = repo_name
        self.language = language
        self.user = None

    def auth(self):

        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                auth = Auth.Token(self.token)
                g = Github(auth=auth)
                self.user = g.get_user()
                print(f'UserName: {self.user.login}')
                break
            except GithubException as e:
                print(f'HTTP status {e.status}: У вас осталось {max_attempts - attempt - 1} попыток.')
                if attempt + 1 < max_attempts:
                    self.token = getpass("🔑 Введите GITHUB ACCESS TOKEN: ")
        else:
            print("Превышено максимальное количество попыток ввода токена.")
            exit(1)

    def create_repo(self):
        repo = self.user.create_repo(
            name=self.repo_name,
            description="Test create repo in class GitHubUtil",
            private=False,
            gitignore_template="Go",
            auto_init=True
        )
        print(f"This is your create repo link {repo.html_url}, {repo.full_name}  good luck!!! [:)]")

    def delete_repo(self):
        repo = self.user.get_repo(self.repo_name)
        repo.delete()
        print(f"delete {self.repo_name}")

    def repo_list(self):
        repos = self.user.get_repos()
        for repo in repos:
            print(f'Repository: {repo.full_name} - Language: {repo.language}')


if __name__ == "__main__":
    init = GitHubUtil("Mher")
    init.auth()
    init.create_repo()
    init.repo_list()
    init.delete_repo()
