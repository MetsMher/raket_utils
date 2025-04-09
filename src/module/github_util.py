from github import Github
from github import Auth
from github.GithubException import BadCredentialsException

from os import getenv
import getpass


token = getenv("GITHUB_TOKEN")

if not token:
    print("Введите токен:")
    token = getpass.getpass()
else:
    print("Токен найден.")

try:

    auth = Auth.Token(token)
    

    g = Github(auth=auth)
    repo = g.get_repo("MetsMher/raket_utils") 

    print(f"This is repo: {repo.html_url}")
    
except BadCredentialsException as e:
    print(f"Неверный токен! Ошибка: {e}")
except Exception as e:
    print(f"Произошла неожиданная ошибка: {e}")