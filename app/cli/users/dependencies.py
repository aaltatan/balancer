# ruff: noqa: B008
from collections.abc import Generator
from typing import Any

import typer
from pydantic import SecretStr, ValidationError
from rich.console import Console
from sqlalchemy.orm import Session
from typer_di import Depends

from app.db import get_db
from app.models.user import UserCreate
from app.services.admin import AdminService

from .inputs import FirstnameOpt, LastnameOpt, PasswordOpt, UsernameOpt


def get_admin_service(db: Generator[Session, Any, None] = Depends(get_db)) -> AdminService:
    return AdminService(next(db))


def get_create_superuser_schema(
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
