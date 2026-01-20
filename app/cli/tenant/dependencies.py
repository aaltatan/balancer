from collections.abc import Generator
from typing import Any

import typer
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typer_di import Depends

from app.db import get_db
from app.schemas.tenant import TenantCreateSchema, TenantUpdateSchema
from app.services.tenant import TenantService

from .inputs import (
    AddressOpt,
    CityOpt,
    CodeArg,
    CountryOpt,
    NameArg,
    NotesOpt,
    OptionalAddressOpt,
    OptionalCityOpt,
    OptionalCountryOpt,
    OptionalNameArg,
    OptionalNotesOpt,
    OptionalPhoneOpt,
    OptionalValidUntilArg,
    PhoneOpt,
    ValidUntilArg,
)


def get_tenant_service(db: Generator[Session, Any, None] = Depends(get_db)) -> TenantService:  # noqa: B008
    return TenantService(next(db))


def get_create_schema(  # noqa: PLR0913
    name: NameArg,
    code: CodeArg,
    valid_until: ValidUntilArg,
    address: AddressOpt = "",
    city: CityOpt = "",
    country: CountryOpt = "",
    phone: PhoneOpt = "",
    notes: NotesOpt = "",
) -> TenantCreateSchema:
    try:
        return TenantCreateSchema(
            name=name,
            code=code,
            valid_until=valid_until,
            address=address,
            city=city,
            country=country,
            phone=phone,
            notes=notes,
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def get_update_schema(  # noqa: PLR0913
    name: OptionalNameArg = None,
    valid_until: OptionalValidUntilArg = None,
    address: OptionalAddressOpt = None,
    city: OptionalCityOpt = None,
    country: OptionalCountryOpt = None,
    phone: OptionalPhoneOpt = None,
    notes: OptionalNotesOpt = None,
) -> TenantUpdateSchema:
    try:
        return TenantUpdateSchema(
            name=name,
            valid_until=valid_until,
            address=address,
            city=city,
            country=country,
            phone=phone,
            notes=notes,
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e
