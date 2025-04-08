import typer

from typing import Optional

from gitlab_util import GitlabUtil

from logger import logger


def create_project(name, lang: Optional[str]):
    inst = GitlabUtil(name, lang)
    inst.auth()
    inst.create()
    inst.add_base_files_for_project()
    inst.add_branches()
    inst.protected_branches()
    logger.info("Процесс завершен успешно")


def delete_project(name: str):
    inst = GitlabUtil(name)
    inst.auth()
    inst.delete()


app = typer.Typer(add_completion=False)


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
def delete(name: str = typer.Option(..., "--name", "-n", help="Name of the project.", show_default=False)):
    """
    Команда для удаления проекта.

    Аргумент:
    name: Имя проекта (--name, -n)
    """

    delete_project(name)
