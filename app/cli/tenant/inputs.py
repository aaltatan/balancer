from datetime import datetime
from typing import Annotated

import typer

CodeArg = Annotated[str, typer.Argument(help="Tenant code")]

NameArg = Annotated[str, typer.Argument(help="Tenant name")]
OptionalNameArg = Annotated[str | None, typer.Argument(help="Tenant name")]

ValidUntilArg = Annotated[datetime, typer.Argument(help="Tenant valid until date")]
OptionalValidUntilArg = Annotated[datetime | None, typer.Argument(help="Tenant valid until date")]

AddressOpt = Annotated[str, typer.Option("--address", help="Tenant address")]
OptionalAddressOpt = Annotated[str | None, typer.Option("--address", help="Tenant address")]

CityOpt = Annotated[str, typer.Option("--city", help="Tenant city")]
OptionalCityOpt = Annotated[str | None, typer.Option("--city", help="Tenant city")]

CountryOpt = Annotated[str, typer.Option("--country", help="Tenant country")]
OptionalCountryOpt = Annotated[str | None, typer.Option("--country", help="Tenant country")]

PhoneOpt = Annotated[str, typer.Option("--phone", help="Tenant phone")]
OptionalPhoneOpt = Annotated[str | None, typer.Option("--phone", help="Tenant phone")]

NotesOpt = Annotated[str, typer.Option("--notes", help="Tenant notes")]
OptionalNotesOpt = Annotated[str | None, typer.Option("--notes", help="Tenant notes")]
