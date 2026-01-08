import uuid
from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

NameFld = Annotated[str, Field(min_length=4, max_length=255, examples=["Dabbagh"])]
ValidFromFld = Annotated[datetime, Field(examples=["2023-01-01"])]
ValidToFld = Annotated[datetime, Field(examples=["2023-01-31"])]


class TenantBase(BaseModel):
    name: NameFld
    valid_from: ValidFromFld
    valid_to: ValidToFld

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        if self.valid_from >= self.valid_to:
            message = "Valid from date must be before valid to date."
            raise ValueError(message)

        return self


class _UserRead(BaseModel):
    uid: uuid.UUID
    fullname: str
    is_active: bool
    role: str

    is_superuser: bool
    is_tenant_superuser: bool
    is_tenant_user: bool

    created_at: datetime
    updated_at: datetime


class TenantRead(TenantBase):
    uid: uuid.UUID
    disabled: bool
    slug: str

    created_at: datetime
    updated_at: datetime

    is_active: bool
    users: list[_UserRead]


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: NameFld | None = None
    valid_from: ValidFromFld | None = None
    valid_to: ValidToFld | None = None
