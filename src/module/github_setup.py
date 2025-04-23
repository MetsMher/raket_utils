from github_util import GitHubUtil

from typing import Optional


def create_project_github(name: str, language: Optional[str] = None):
    try:
        util = GitHubUtil(name, language)
        util.auth()
        util.create_repo()
        with util.managed_project():
            util.add_base_files_for_project()
            util.create_branches()  
        # logger.info("✅ Всё успешно завершено! Проект создан.")
    except Exception as e:
        exit(1)
        # raise
        # logger.error(f"❌ Ошибка в процессе: {e}")

def delete_project_github(name: str):
    util = GitHubUtil(name)
    util.auth()
    with util.managed_project():
        util.delete_repo()