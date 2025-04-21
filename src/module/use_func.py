from gitlab_util import GitlabUtil

from github_util import GitHubUtil

from typing import Optional

from logger import logger


def create_project(name, language: Optional[str], platform: Optional[str] = None):
    """
    Создание проекта на GitLab.
    :param name: Имя проекта
    :param language: Язык проекта
    :param platform: Платформа (GitLab или GitHub)
    """
    if platform == "gitlab".lower():
        create_project_gitlab(name, language)
    elif platform == "github".lower():
        create_project_github(name, language=None)
    else:
        logger.error("Платформа не поддерживается. Выберите GitLab или GitHub.")
        # exit(1)
        # raise ValueError("Платформа не поддерживается. Выберите GitLab или GitHub.")


def delete_project(name, platform: Optional[str] = None):
    """
    Удаление проекта на GitLab.
    :param name: Имя проекта
    :param platform: Платформа (GitLab или GitHub)
    """
    if platform == "gitlab".lower():
        delete_project_gitlab(name)
    elif platform == "github".lower():
        delete_project_github(name)
    else:
        logger.error(f"'{platform}' Платформа не поддерживается. Выберите GitLab или GitHub.")
        # exit(1)
        # raise ValueError("Платформа не поддерживается. Выберите GitLab или GitHub.")

        
def create_project_gitlab(name, language: Optional[str]):
    try:
        util = GitlabUtil(name, language)
        util.auth()
        util.create_project()
        with util.managed_project():
            util.protected_branches_project()
            util.add_base_files_for_project()
            util.add_branches_project()     
            util.get_project_info()
        logger.info("✅ Всё успешно завершено! Проект создан.")
    except Exception as e:
        exit(1)
        # raise
        # logger.error(f"❌ Ошибка в процессе: {e}")


def delete_project_gitlab(name: str):
    util = GitlabUtil(name)
    util.auth()
    with util.managed_project():
        util.delete_project()


def create_project_github(name: str, language: Optional[str] = None):
    try:
        util = GitHubUtil(name)
        util.auth()
        util.create_repo()
        with util.managed_project():
            util.create_branches()     
        logger.info("✅ Всё успешно завершено! Проект создан.")
    except Exception as e:
        exit(1)
        # raise
        # logger.error(f"❌ Ошибка в процессе: {e}")

def delete_project_github(name: str):
    util = GitHubUtil(name)
    util.auth()
    with util.managed_project():
        util.delete_repo()