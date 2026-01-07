# ruff: noqa: B008
import typer
from rich.console import Console
from typer_di import Depends, TyperDI

from app.models.user import UserCreate
from app.services.admin import AdminService, UserAlreadyExistsError

from .dependencies import get_admin_service, get_console, get_create_superuser_schema

app = TyperDI(name="users")


@app.command(name="createsuperuser")
def create_superuser(
    console: Console = Depends(get_console),
    service: AdminService = Depends(get_admin_service),
    user: UserCreate = Depends(get_create_superuser_schema),
) -> None:
    try:
        user_db = service.create_superuser(user, user.password.get_secret_value())
    except UserAlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Superuser '{user_db.username}' created successfully[/bold green]")
