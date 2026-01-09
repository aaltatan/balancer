# ruff: noqa: B008
import typer
from rich.console import Console
from typer_di import Depends, TyperDI

from app.models.user import ResetPassword, UserCreate
from app.services.generic_user import MoreThanOneSuperuserError, UserNotFoundError
from app.services.superuser import SuperuserService

from .dependencies import (
    get_console,
    get_create_schema,
    get_reset_password_schema,
    get_superuser_service,
)

app = TyperDI()


@app.callback()
def main() -> None:
    """Superuser CLI (access from root user only)."""


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
    except MoreThanOneSuperuserError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' created successfully[/bold green]"
    )


@app.command(name="reset-password")
def reset_superuser_password(
    console: Console = Depends(get_console),
    superuser_service: SuperuserService = Depends(get_superuser_service),
    schema: ResetPassword = Depends(get_reset_password_schema),
):
    try:
        superuser = superuser_service.reset_password(schema.new_password.get_secret_value())
    except UserNotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Password reset for user '{superuser.username}' successfully[/bold green]"
    )
