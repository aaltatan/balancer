from typing import Annotated

import typer
from pydantic import SecretStr, ValidationError
from typer_di import Depends, TyperDI

from balancer.domain.exceptions import AlreadyExistsError, NotFoundError
from balancer.domain.schemas.user import ResetPassword, UserCreate, UserUpdate
from balancer.domain.services.generic_user import GenericUserService
from balancer.domain.services.superuser import SuperuserService
from balancer.entrypoint.cli.dependencies import (
    ConsoleDI,
    HasherFnDI,
    ListCommandOptionsDI,
    SessionDI,
)
from balancer.entrypoint.cli.table import get_table

_PasswordOpt = Annotated[
    str, typer.Option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
]


def _get_service(session: SessionDI, hasher_fn: HasherFnDI) -> SuperuserService:
    return SuperuserService(session, GenericUserService(session, hasher_fn))


def _get_create_schema(
    username: Annotated[str, typer.Option("--username", "-u")],
    firstname: Annotated[str, typer.Option("--firstname", "-f")],
    lastname: Annotated[str, typer.Option("--lastname", "-l")],
    password: _PasswordOpt,
) -> UserCreate:
    try:
        return UserCreate(
            username=username, firstname=firstname, lastname=lastname, password=SecretStr(password)
        )
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def _get_update_schema(
    firstname: Annotated[str | None, typer.Option("--firstname", "-f")] = None,
    lastname: Annotated[str | None, typer.Option("--lastname", "-l")] = None,
) -> UserUpdate:
    try:
        return UserUpdate(firstname=firstname, lastname=lastname)
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


def _get_reset_password_schema(new_password: _PasswordOpt) -> ResetPassword:
    try:
        return ResetPassword(new_password=SecretStr(new_password))
    except ValidationError as e:
        raise typer.BadParameter(str(e)) from e


app = TyperDI(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Superuser CLI (access from root user only)."""


@app.command(name="list")
@app.command(name="ls")
def list_superusers(
    console: ConsoleDI,
    service: Annotated[SuperuserService, Depends(_get_service)],
    options: ListCommandOptionsDI,
) -> None:
    """Get a list of all superusers."""
    try:
        users = service.get_all()
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    table = get_table(
        {"attr_name": "username"},
        {"attr_name": "fullname"},
        {"attr_name": "is_active", "header": "active"},
        {
            "attr_name": "role",
            "renderer_fn": lambda role: "💪" if role in ("superuser", "tenant-superuser") else "👤",
        },
        {"attr_name": "uid", "header": "uuid", "style": "yellow"},
        objects=users,
        title="users",
        add_index=options.add_index,
        show_lines=options.show_lines,
        border_style=options.border_style,
    )

    console.print(table)


@app.command(name="create")
@app.command(name="add")
def create_superuser(
    console: ConsoleDI,
    service: Annotated[SuperuserService, Depends(_get_service)],
    schema: Annotated[UserCreate, Depends(_get_create_schema)],
) -> None:
    """Create a new superuser."""
    try:
        superuser_db = service.create(
            schema=schema, plain_password=schema.password.get_secret_value()
        )
    except AlreadyExistsError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' created successfully[/bold green]"
    )


@app.command(name="update")
@app.command(name="edit")
def update_superuser(
    console: ConsoleDI,
    username: Annotated[str, typer.Argument()],
    schema: Annotated[UserUpdate, Depends(_get_update_schema)],
    service: Annotated[SuperuserService, Depends(_get_service)],
) -> None:
    """Update an existing superuser."""
    try:
        superuser_db = service.update(username, schema)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' updated successfully[/bold green]"
    )


@app.command(name="activate")
def activate_superuser(
    console: ConsoleDI,
    username: Annotated[str, typer.Argument()],
    service: Annotated[SuperuserService, Depends(_get_service)],
) -> None:
    """Activate a superuser."""
    try:
        superuser_db = service.activate(username)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' activated successfully[/bold green]"
    )


@app.command(name="deactivate")
def deactivate_superuser(
    console: ConsoleDI,
    username: Annotated[str, typer.Argument()],
    service: Annotated[SuperuserService, Depends(_get_service)],
) -> None:
    """Deactivate a superuser."""
    try:
        superuser_db = service.deactivate(username)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Superuser '{superuser_db.username}' deactivated successfully[/bold green]"
    )


@app.command(name="delete")
@app.command(name="rm")
def delete_superuser(
    console: ConsoleDI,
    username: Annotated[str, typer.Argument()],
    service: Annotated[SuperuserService, Depends(_get_service)],
) -> None:
    """Delete a superuser."""
    try:
        service.delete(username)
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(f"[bold green]Superuser '{username}' deleted successfully[/bold green]")


@app.command(name="reset-password")
def reset_superuser_password(
    console: ConsoleDI,
    username: Annotated[str, typer.Argument()],
    service: Annotated[SuperuserService, Depends(_get_service)],
    schema: Annotated[ResetPassword, Depends(_get_reset_password_schema)],
) -> None:
    """Reset a superuser password."""
    try:
        superuser = service.reset_password(username, schema.new_password.get_secret_value())
    except NotFoundError as e:
        raise typer.BadParameter(str(e)) from e

    console.print(
        f"[bold green]Password reset for user '{superuser.username}' successfully[/bold green]"
    )
