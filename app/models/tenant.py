import re
import uuid
from datetime import datetime
from typing import Annotated, Self

import pytz
from pydantic import AfterValidator, BaseModel, Field, model_validator

from app.utils.timezone import get_default_tz_now


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


class TenantBase(BaseModel):
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


class _UserRead(BaseModel):
    uid: uuid.UUID
    fullname: str
    role: str

    created_at: datetime
    updated_at: datetime


class TenantRead(TenantBase):
    uid: uuid.UUID
    code: str

    created_at: datetime
    updated_at: datetime

    users: list[_UserRead]


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: NameFld | None = None
    valid_until: ValidUntilFld | None = None

    address: AddressFld | None = None
    city: CityFld | None = None
    country: CountryFld | None = None
    phone: PhoneFld | None = None
    notes: NotesFld | None = None
