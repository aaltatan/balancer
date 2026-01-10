# ruff: noqa: B008
import typer
from rich.console import Console
from typer_di import Depends, TyperDI

from app.models.user import ResetPassword, UserCreate, UserUpdate
from app.services.generic_user import UserAlreadyExistsError, UserNotFoundError
from app.services.superuser import SuperuserService

from .dependencies import (
    get_console,
    get_create_schema,
    get_reset_password_schema,
    get_superuser_service,
    get_user_update_schema,
)
from .inputs import UsernameArg
from .table import get_table

app = TyperDI()


@app.callback()
def main() -> None:
    """Superuser CLI (access from root user only)."""


@app.command(name="list")
def list_superusers(
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
) -> None:
    try:
        users = superuser_service.get_all()
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(get_table(users))


@app.command(name="create")
def create_superuser(
    console: Console = Depends(get_console),
    superuser: UserCreate = Depends(get_create_schema),
    superuser_service: SuperuserService = Depends(get_superuser_service),
) -> None:
    try:
        password = superuser.password.get_secret_value()
        superuser_db = superuser_service.create(
            superuser.username, superuser.firstname, superuser.lastname, password
        )
    except UserAlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' created successfully[/bold green]"
    )


@app.command(name="update")
def update_superuser(
    username: UsernameArg,
    console: Console = Depends(get_console),
    superuser: UserUpdate = Depends(get_user_update_schema),
    superuser_service: SuperuserService = Depends(get_superuser_service),
):
    try:
        superuser_db = superuser_service.update(username, superuser.firstname, superuser.lastname)
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' updated successfully[/bold green]"
    )


@app.command(name="activate")
def activate_superuser(
    username: UsernameArg,
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
):
    try:
        superuser_db = superuser_service.activate(username)
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' activated successfully[/bold green]"
    )


@app.command(name="deactivate")
def deactivate_superuser(
    username: UsernameArg,
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
):
    try:
        superuser_db = superuser_service.deactivate(username)
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' deactivated successfully[/bold green]"
    )


@app.command(name="delete")
def delete_superuser(
    username: UsernameArg,
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
):
    try:
        superuser_service.delete(username)
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Superuser '{username}' deleted successfully[/bold green]")


@app.command(name="reset-password")
def reset_superuser_password(
    username: UsernameArg,
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
    schema: ResetPassword = Depends(get_reset_password_schema),
):
    try:
        superuser = superuser_service.reset_password(
            username, schema.new_password.get_secret_value()
        )
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Password reset for user '{superuser.username}' successfully[/bold green]"
    )
