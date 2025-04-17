import typer

from typing import Optional

from gitlab_util import GitlabUtil

from logger import logger


def create_project(name, lang: Optional[str]):
    try:
        util = GitlabUtil(name, lang)
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


def delete_project(name: str):
    util = GitlabUtil(name)
    util.auth()
    with util.managed_project():
        util.delete_project()


app = typer.Typer(add_completion=False)

@app.command()
def create_org(name: str = typer.Option(..., "--name", "-n", help="Name of the group.", show_default=False)):
        """
    Команда для создания группы.

    Аргументы:
    name: Имя группы
        """
    

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
def delete(name: str = typer.Option(...,
                                    "--name", "-n",
                                    help="Name of the project.",
                                    show_default=False)
           ):
    """
    Команда для удаления проекта.

    Аргумент:
    name: Имя проекта (--name, -n)
    """

    delete_project(name)
