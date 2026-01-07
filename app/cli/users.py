# ruff: noqa: B008
from collections.abc import Generator
from typing import Annotated, Any

import typer
from pydantic import SecretStr, ValidationError
from rich.console import Console
from sqlalchemy.orm import Session
from typer_di import Depends, TyperDI

from app.db import get_db
from app.models.user import UserCreate
from app.services.user import UserAlreadyExistsError, UserService

app = TyperDI(name="users")

UsernameOpt = Annotated[str, typer.Option("--username", "-u")]
FirstnameOpt = Annotated[str, typer.Option("--firstname", "-f")]
LastnameOpt = Annotated[str, typer.Option("--lastname", "-l")]
PasswordOpt = Annotated[
    str, typer.Option("--password", prompt="Password", hide_input=True, confirmation_prompt=True)
]


def get_user_service(db: Generator[Session, Any, None] = Depends(get_db)) -> UserService:
    return UserService(next(db))


def get_create_user_schema(
    username: UsernameOpt, firstname: FirstnameOpt, lastname: LastnameOpt, password: PasswordOpt
) -> UserCreate:
    try:
        return UserCreate(
            username=username, firstname=firstname, lastname=lastname, password=SecretStr(password)
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_console() -> Console:
    return Console()


@app.command(name="createsuperuser")
def create_superuser(
    console: Console = Depends(get_console),
    service: UserService = Depends(get_user_service),
    user: UserCreate = Depends(get_create_user_schema),
) -> None:
    try:
        user_db = service.create_superuser(user, user.password.get_secret_value())
    except UserAlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Superuser '{user_db.username}' created successfully[/bold green]")
