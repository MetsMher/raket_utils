from gitlab_setup import create_project_gitlab, delete_project_gitlab

from github_setup import create_project_github, delete_project_github

from logger import logger

from typing import Optional 

import typer


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
        create_project_github(name, language)
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