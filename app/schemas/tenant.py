import re
import uuid
from datetime import datetime
from typing import Annotated, Self

import pytz
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from app.core.timezone import get_default_tz_now


def validate_code(code: str) -> str:
    if len(code) != 4:
        message = "code must be 4 characters long"
        raise ValueError(message)

    if not re.match(r"^[a-z]{4}$", code):
        message = "code must be 4 uppercase letters"
        raise ValueError(message)

    return code


NameFld = Annotated[str, Field(min_length=4, max_length=255, examples=["Dabbagh"])]
CodeFld = Annotated[
    str, Field(min_length=4, max_length=4, examples=["dbgh"]), AfterValidator(validate_code)
]
ValidUntilFld = Annotated[datetime, Field(examples=["2028-12-31"])]

AddressFld = Annotated[str, Field(max_length=255, examples=["Alneil Street"])]
CityFld = Annotated[str, Field(max_length=255, examples=["Hamah"])]
CountryFld = Annotated[str, Field(max_length=255, examples=["Syria"])]
PhoneFld = Annotated[str, Field(min_length=14, max_length=255, examples=["00963947302503"])]
NotesFld = Annotated[str, Field(max_length=255, examples=[""])]


class TenantBaseSchema(BaseModel):
    name: NameFld
    code: CodeFld
    valid_until: ValidUntilFld

    address: AddressFld = ""
    city: CityFld = ""
    country: CountryFld = ""
    phone: PhoneFld = ""
    notes: NotesFld = ""

    @model_validator(mode="after")
    def validate_name(self) -> Self:
        if get_default_tz_now() > pytz.utc.localize(self.valid_until):
            message = "valid_until must be in the future"
            raise ValueError(message)

        return self


class _UserReadSchema(BaseModel):
    uid: uuid.UUID
    fullname: str
    role: str

    created_at: datetime
    updated_at: datetime


class TenantExportSchema(TenantBaseSchema):
    model_config = ConfigDict(from_attributes=True)


class TenantReadSchema(TenantBaseSchema):
    uid: uuid.UUID
    code: str

    created_at: datetime
    updated_at: datetime

    users: list[_UserReadSchema]


class TenantCreateSchema(TenantBaseSchema):
    pass


class TenantUpdateSchema(BaseModel):
    name: NameFld | None = None
    valid_until: ValidUntilFld | None = None

    address: AddressFld | None = None
    city: CityFld | None = None
    country: CountryFld | None = None
    phone: PhoneFld | None = None
    notes: NotesFld | None = None


class TenantFilterSchema(BaseModel):
    search__contains: str | None
    search__notcontains: str | None
    code__eq: str | None
    code__ne: str | None
    phone__contains: str | None
    phone__notcontains: str | None
    phone__eq: str | None
    valid_until__eq: datetime | None
    valid_until__ne: datetime | None
    valid_until__gt: datetime | None
    valid_until__gte: datetime | None
    valid_until__lt: datetime | None
    valid_until__lte: datetime | None
