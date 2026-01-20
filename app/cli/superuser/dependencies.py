# ruff: noqa: B008
from collections.abc import Callable, Generator
from typing import Any

import typer
from pydantic import SecretStr, ValidationError
from sqlalchemy.orm import Session
from typer_di import Depends

from app.db import get_db
from app.dependencies import get_hasher_fn
from app.schemas.user import ResetPasswordSchema, UserCreateSchema, UserUpdateSchema
from app.services.generic_user import GenericUserService
from app.services.superuser import SuperuserService

from .inputs import (
    FirstnameOpt,
    LastnameOpt,
    OptionalFirstnameOpt,
    OptionalLastnameOpt,
    PasswordOpt,
    UsernameOpt,
)


def get_superuser_service(
    db: Generator[Session, Any, None] = Depends(get_db),
    hasher_fn: Callable[[str], str] = Depends(get_hasher_fn),
) -> SuperuserService:
    session = next(db)
    return SuperuserService(session, GenericUserService(session, hasher_fn))


def get_create_schema(
    username: UsernameOpt, firstname: FirstnameOpt, lastname: LastnameOpt, password: PasswordOpt
) -> UserCreateSchema:
    try:
        return UserCreateSchema(
            username=username, firstname=firstname, lastname=lastname, password=SecretStr(password)
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_user_update_schema(
    firstname: OptionalFirstnameOpt = None, lastname: OptionalLastnameOpt = None
) -> UserUpdateSchema:
    try:
        return UserUpdateSchema(firstname=firstname, lastname=lastname)
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_reset_password_schema(new_password: PasswordOpt) -> ResetPasswordSchema:
    try:
        return ResetPasswordSchema(new_password=SecretStr(new_password))
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e
