# ruff: noqa: B008
from collections.abc import Generator
from typing import Any

import typer
from pydantic import SecretStr, ValidationError
from rich.console import Console
from sqlalchemy.orm import Session
from typer_di import Depends

from app.db import get_db
from app.models.user import ResetPassword, UserCreate
from app.services.generic_user import GenericUserService
from app.services.superuser import SuperuserService

from .inputs import FirstnameOpt, LastnameOpt, PasswordOpt, UsernameOpt


def get_superuser_service(db: Generator[Session, Any, None] = Depends(get_db)) -> SuperuserService:
    session = next(db)
    return SuperuserService(session, GenericUserService(session))


def get_create_schema(
    username: UsernameOpt, firstname: FirstnameOpt, lastname: LastnameOpt, password: PasswordOpt
) -> UserCreate:
    try:
        return UserCreate(
            username=username, firstname=firstname, lastname=lastname, password=SecretStr(password)
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_reset_password_schema(new_password: PasswordOpt) -> ResetPassword:
    try:
        return ResetPassword(new_password=SecretStr(new_password))
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_console() -> Console:
    return Console()
