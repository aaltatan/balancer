import re
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field

from app.db.permission import Permission
from app.db.user import Role

from ._fields import PasswordFld


def validate_username(value: str) -> str:
    if not re.match(r"^[a-z][a-z0-9_]+$", value):
        message = (
            "Username must be lowercase letters, numbers, or underscores, "
            "and must start with a letter."
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
    is_active: bool
    role: Role

    is_superuser: bool
    is_tenant_superuser: bool
    is_tenant_user: bool

    created_at: datetime
    updated_at: datetime


class _TenantRead(BaseModel):
    uid: uuid.UUID
    name: str
    valid_from: datetime
    valid_to: datetime
    disabled: bool
    slug: str

    created_at: datetime
    updated_at: datetime

    is_active: bool


class UserReadWithTenant(UserReadWithoutRelations):
    tenant: _TenantRead


class UserRead(UserReadWithTenant):
    permissions: list[PermissionRead] = Field(default_factory=list)


class UserCreate(UserBase):
    password: PasswordFld
    permissions: set[Permission] = Field(
        default_factory=set,
        exclude=True,
        examples=[[Permission.USERS_READ, Permission.USERS_CREATE]],
    )


class UserUpdate(BaseModel):
    firstname: FirstnameFld | None = None
    lastname: LastnameFld | None = None


class ResetPassword(BaseModel):
    new_password: PasswordFld
