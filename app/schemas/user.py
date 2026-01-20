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


class PermissionReadSchema(BaseModel):
    name: Permission


class UserBaseSchema(BaseModel):
    username: UsernameFld
    firstname: FirstnameFld
    lastname: LastnameFld


class UserReadWithoutRelationsSchema(UserBaseSchema):
    uid: uuid.UUID
    fullname: str
    role: Role

    created_at: datetime
    updated_at: datetime


class _TenantReadSchema(BaseModel):
    uid: uuid.UUID
    name: str
    code: str


class UserReadWithTenant(UserReadWithoutRelationsSchema):
    tenant: _TenantReadSchema | None = None


class UserReadSchema(UserReadWithTenant):
    permissions: list[PermissionReadSchema] = Field(default_factory=list)


class UserCreateSchema(UserBaseSchema):
    password: PasswordFld
    permissions: Annotated[
        set[Permission],
        Field(exclude=True, examples=[[Permission.USERS_READ, Permission.USERS_CREATE]]),
    ] = set()


class UserUpdateSchema(BaseModel):
    firstname: FirstnameFld | None = None
    lastname: LastnameFld | None = None


class ResetPasswordSchema(BaseModel):
    new_password: PasswordFld


class UserFilterSchema(BaseModel):
    search__contains: str | None
    search__notcontains: str | None
    username__eq: str | None
    username__ne: str | None
    firstname__eq: str | None
    firstname__ne: str | None
    lastname__eq: str | None
    lastname__ne: str | None
    is_active__eq: bool | None
    is_active__ne: bool | None
    role__eq: str | None
    role__ne: str | None
    created_at__eq: datetime | None
    created_at__ne: datetime | None
    created_at__gt: datetime | None
    created_at__gte: datetime | None
    created_at__lt: datetime | None
    created_at__lte: datetime | None
    updated_at__eq: datetime | None
    updated_at__ne: datetime | None
    updated_at__gt: datetime | None
    updated_at__gte: datetime | None
    updated_at__lt: datetime | None
    updated_at__lte: datetime | None
