from gitlab_util import GitlabUtil
from typing import Optional

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
        # logger.info("✅ Всё успешно завершено! Проект создан.")
    except Exception as e:
        exit(1)
        # raise
        # logger.error(f"❌ Ошибка в процессе: {e}")


def delete_project_gitlab(name: str):
    util = GitlabUtil(name)
    util.auth()
    with util.managed_project():
        util.delete_project()
