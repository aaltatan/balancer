import re
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field

from app.constants import USERNAME_REGEX
from app.db.permission import Permission
from app.db.user import Role

from ._fields import PasswordFld


def validate_username(value: str) -> str:
    if not re.match(USERNAME_REGEX, value):
        message = (
            "Username must be lowercase letters or numbers only, "
            "if the username of two words, it must be like this: first.last or first_last, "
            "it can't be more than two words with a underscore or dot in between, "
            "and it must start with a letter."
        )
        raise ValueError(message)

    return value


def title_string(value: str) -> str:
    return value.strip().title()


UsernameFld = Annotated[
    str,
    Field(min_length=4, max_length=255, examples=["abdullah_altatan"]),
    AfterValidator(validate_username),
]

FirstnameFld = Annotated[
    str,
    Field(min_length=4, max_length=255, examples=["Abdullah"]),
    BeforeValidator(title_string),
]

LastnameFld = Annotated[
    str,
    Field(min_length=4, max_length=255, examples=["Altatan"]),
    BeforeValidator(title_string),
]


class PermissionRead(BaseModel):
    name: Permission


class UserBase(BaseModel):
    username: UsernameFld
    firstname: FirstnameFld
    lastname: LastnameFld


class UserReadWithoutRelations(UserBase):
    uid: uuid.UUID
    fullname: str
    role: Role

    created_at: datetime
    updated_at: datetime


class _TenantRead(BaseModel):
    uid: uuid.UUID
    name: str
    valid_from: datetime
    valid_to: datetime
    slug: str

    created_at: datetime
    updated_at: datetime


class UserReadWithTenant(UserReadWithoutRelations):
    tenant: _TenantRead | None = None


class UserRead(UserReadWithTenant):
    permissions: list[PermissionRead] = Field(default_factory=list)


class UserCreate(UserBase):
    password: PasswordFld
    permissions: Annotated[
        set[Permission],
        Field(exclude=True, examples=[[Permission.USERS_READ, Permission.USERS_CREATE]]),
    ] = set()


class UserUpdate(BaseModel):
    firstname: FirstnameFld | None = None
    lastname: LastnameFld | None = None


class ResetPassword(BaseModel):
    new_password: PasswordFld
