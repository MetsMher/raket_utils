from typing import Optional
import typer


def type_example(name: str, formal: bool = False, intro: Optional[str] = None):
    pass

if __name__ == "__main__":
    typer.run(type_example)