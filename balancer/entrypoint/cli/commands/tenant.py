# ruff: noqa: B008

from datetime import datetime
from typing import Annotated

import typer
from pydantic import ValidationError
from typer_di import Depends, TyperDI

from balancer.domain.exceptions import AlreadyExistsError, CannotDeleteError, NotFoundError
from balancer.domain.schemas.tenant import TenantCreate, TenantUpdate
from balancer.domain.services.tenant import TenantService
from balancer.entrypoint.cli.dependencies import ConsoleDI, ListCommandOptionsDI, SessionDI
from balancer.entrypoint.cli.table import get_table

_CodeArg = Annotated[str, typer.Argument(help="Tenant code")]


def _get_service(session: SessionDI) -> TenantService:
    return TenantService(session)


def _get_create_schema(  # noqa: PLR0913
    name: Annotated[str, typer.Argument(help="Tenant name")],
    code: _CodeArg,
    valid_until: Annotated[datetime, typer.Argument(help="Tenant valid until date")],
    address: Annotated[str, typer.Option("--address", help="Tenant address")] = "",
    city: Annotated[str, typer.Option("--city", help="Tenant city")] = "",
    country: Annotated[str, typer.Option("--country", help="Tenant country")] = "",
    phone: Annotated[str, typer.Option("--phone", help="Tenant phone")] = "",
    notes: Annotated[str, typer.Option("--notes", help="Tenant notes")] = "",
) -> TenantCreate:
    try:
        return TenantCreate(
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


def _get_update_schema(  # noqa: PLR0913
    name: Annotated[str | None, typer.Argument(help="Tenant name")] = None,
    valid_until: Annotated[datetime | None, typer.Argument(help="Tenant valid until date")] = None,
    address: Annotated[str | None, typer.Option("--address", help="Tenant address")] = None,
    city: Annotated[str | None, typer.Option("--city", help="Tenant city")] = None,
    country: Annotated[str | None, typer.Option("--country", help="Tenant country")] = None,
    phone: Annotated[str | None, typer.Option("--phone", help="Tenant phone")] = None,
    notes: Annotated[str | None, typer.Option("--notes", help="Tenant notes")] = None,
) -> TenantUpdate:
    try:
        return TenantUpdate(
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


app = TyperDI(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Tenant CLI (access from root user only)."""


@app.command(name="list")
@app.command(name="ls")
def list_tenants(
    console: ConsoleDI,
    options: ListCommandOptionsDI,
    service: TenantService = Depends(_get_service),
) -> None:
    """List all tenants."""
    items, _ = service.get_all()

    table = get_table(
        {"attr_name": "code"},
        {"attr_name": "name"},
        {"attr_name": "valid_until"},
        {"attr_name": "is_active", "header": "active"},
        {"attr_name": "uid", "header": "uuid", "style": "yellow"},
        objects=items,
        title="Tenants",
        add_index=options.add_index,
        show_lines=options.show_lines,
        border_style=options.border_style,
    )

    console.print(table)


@app.command(name="create")
@app.command(name="add")
def create_tenant(
    console: ConsoleDI,
    service: TenantService = Depends(_get_service),
    create_schema: TenantCreate = Depends(_get_create_schema),
) -> None:
    """Create a new tenant."""
    try:
        tenant_db = service.create(create_schema)
    except AlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' created successfully[/bold green]")


@app.command(name="update")
@app.command(name="edit")
def update_tenant(
    code: _CodeArg,
    console: ConsoleDI,
    service: TenantService = Depends(_get_service),
    update_schema: TenantUpdate = Depends(_get_update_schema),
) -> None:
    """Update an existing tenant."""
    try:
        tenant_db = service.update(code, update_schema)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' updated successfully[/bold green]")


@app.command(name="activate")
def activate_tenant(
    code: _CodeArg, console: ConsoleDI, service: TenantService = Depends(_get_service)
) -> None:
    """Activate a tenant by its code."""
    try:
        tenant_db = service.activate(code)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' activated successfully[/bold green]")


@app.command(name="deactivate")
def deactivate_tenant(
    code: _CodeArg, console: ConsoleDI, service: TenantService = Depends(_get_service)
) -> None:
    """Deactivate a tenant by its code."""
    try:
        tenant_db = service.deactivate(code)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' deactivated successfully[/bold green]")


@app.command(name="delete")
@app.command(name="rm")
def delete_tenant(
    code: _CodeArg, console: ConsoleDI, service: TenantService = Depends(_get_service)
) -> None:
    """Delete a tenant by its code."""
    try:
        service.delete(code)
    except (NotFoundError, CannotDeleteError) as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{code}' deleted successfully[/bold green]")
