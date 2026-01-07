import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Self

from pydantic import AfterValidator, BaseModel, Field, model_validator

if TYPE_CHECKING:
    from .user import UserReadWithoutRelations


def validate_valid_from_date(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    if value < datetime.now(tz=timezone.utc):
        message = "Valid from date must be in the future."
        raise ValueError(message)

    return value


def validate_valid_to_date(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    if value < datetime.now(tz=timezone.utc):
        message = "Valid to date must be in the future."
        raise ValueError(message)

    return value


NameFld = Annotated[str, Field(min_length=4, max_length=255, examples=["Dabbagh"])]
ValidFromFld = Annotated[
    datetime, Field(serialization_alias="validFrom"), AfterValidator(validate_valid_from_date)
]
ValidToFld = Annotated[
    datetime, Field(serialization_alias="validTo"), AfterValidator(validate_valid_to_date)
]


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


class TenantReadWithoutRelations(TenantBase):
    uid: uuid.UUID
    disabled: bool
    slug: str

    created_at: datetime
    updated_at: datetime

    is_active: bool


class TenantRead(TenantReadWithoutRelations):
    users: set["UserReadWithoutRelations"]


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: NameFld | None = None
    valid_from: ValidFromFld | None = None
    valid_to: ValidToFld | None = None
