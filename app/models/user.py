import re
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field

from app.db.permission import Permission
from app.db.user import Role

from ._fields import PasswordFld

if TYPE_CHECKING:
    from .tenant import TenantReadWithoutRelations


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


UsernameFld = Annotated[str, Field(min_length=4, max_length=255), AfterValidator(validate_username)]
FirstnameFld = Annotated[str, Field(min_length=4, max_length=255), BeforeValidator(title_string)]
LastnameFld = Annotated[str, Field(min_length=4, max_length=255), BeforeValidator(title_string)]


class PermissionRead(BaseModel):
    uid: uuid.UUID
    name: Permission

    users: list["UserReadWithTenant"] = []


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


class UserReadWithTenant(UserReadWithoutRelations):
    tenant: "TenantReadWithoutRelations"


class UserRead(UserReadWithTenant):
    permissions: set[PermissionRead]


class UserCreate(UserBase):
    password: PasswordFld
    permissions: set[Permission] = Field(default_factory=set)


class UserUpdate(BaseModel):
    firstname: FirstnameFld | None = None
    lastname: LastnameFld | None = None


class ResetPassword(BaseModel):
    new_password: PasswordFld


UserReadWithTenant.model_rebuild()
UserRead.model_rebuild()
PermissionRead.model_rebuild()
