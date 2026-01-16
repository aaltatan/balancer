# ruff: noqa: B008

import typer
from rich.console import Console
from typer_di import Depends, TyperDI

from app.cli.dependencies import get_console
from app.exceptions import AlreadyExistsError, CannotDeleteError, NotFoundError
from app.models.tenant import TenantCreate, TenantUpdate
from app.services.tenant import TenantService

from .dependencies import get_create_schema, get_tenant_service, get_update_schema
from .inputs import CodeArg
from .table import get_table

app = TyperDI()


@app.callback()
def main() -> None:
    """Tenant CLI (access from root user only)."""


@app.command(name="list")
def list_tenants(
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
) -> None:
    items, items_count = service.get_all()
    console.print(get_table(items))
    console.print(f"[bold green]Total items: {items_count}[/bold green]")


@app.command(name="create")
def create_tenant(
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
    create_schema: TenantCreate = Depends(get_create_schema),
):
    try:
        tenant_db = service.create(create_schema)
    except AlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' created successfully[/bold green]")


@app.command(name="update")
def update_tenant(
    code: CodeArg,
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
    update_schema: TenantUpdate = Depends(get_update_schema),
):
    try:
        tenant_db = service.update(code, update_schema)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' updated successfully[/bold green]")


@app.command(name="activate")
def activate_tenant(
    code: CodeArg,
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
):
    try:
        tenant_db = service.activate(code)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' activated successfully[/bold green]")


@app.command(name="deactivate")
def deactivate_tenant(
    code: CodeArg,
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
):
    try:
        tenant_db = service.deactivate(code)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{tenant_db.name}' deactivated successfully[/bold green]")


@app.command(name="delete")
def delete_tenant(
    code: CodeArg,
    console: Console = Depends(get_console),
    service: TenantService = Depends(get_tenant_service),
):
    try:
        service.delete(code)
    except (NotFoundError, CannotDeleteError) as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Tenant '{code}' deleted successfully[/bold green]")
