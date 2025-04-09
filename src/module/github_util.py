from github import Github, Auth

from os import getenv

from getpass import getpass


class GitHubUtil:
    def __init__(self, repo_name, language=None):
        self.token = getenv("GITHUB_TOKEN")
        if not self.token:
            print("GITHUB_TOKEN не найден. Введите токен вручную (осталось 3 попытки).")
            self.token = getpass("🔑 Введите GITHUB ACCESS TOKEN: ")
        self.repo_name = repo_name
        self.language = language
        self.user = None

    def auth(self):
        auth = Auth.Token(self.token)
        g = Github(auth=auth)
        self.user = g.get_user()

    def create_repo(self):
        repo = self.user.create_repo(
            name=self.repo_name,
            description="Test create repo in class GitHubUtil",
            private=False,
            gitignore_template="Go",
            auto_init=True
        )
        print(f"This is your create repo link {repo.html_url}, good luck!!! [:)]")


if __name__ == "__main__":
    init = GitHubUtil("Aparan")
    init.auth()
    init.create_repo()
