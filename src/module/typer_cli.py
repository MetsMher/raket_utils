from use_func import create_project, delete_project

import typer


app = typer.Typer(add_completion=False)


@app.command()
def create(
        platform: str = typer.Option(..., "--platform", "-pl", help="Platform for create project.", show_default=False),
        language: str = typer.Option(..., "--language", "-l", help="Language of the project.", show_default=False),
        name: str = typer.Option(..., "--name", "-n", help="Name of the project.", show_default=False)):
    """
    Команда для создания нового проекта.

    Аргументы:
    name: Имя проекта
    lang: Язык проекта
    """
    create_project(name, language, platform)


@app.command()
def delete(
        name: str = typer.Option(..., "--name", "-n", help="Name of the project.", show_default=False),
        platform: str = typer.Option(..., "--platform", "-pl", help="Platform for create project.", show_default=False)):
    """
    Команда для удаления проекта.
    Аргументы:
    name: Имя проекта
    """

    delete_project(name, platform)