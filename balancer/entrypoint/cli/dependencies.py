from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

import typer
from rich.console import Console
from sqlalchemy.orm import Session
from typer_di import Depends

from balancer.domain.models import get_db
from balancer.utils.security import hash_password, verify_password

from .table import TableBorderStyle


@dataclass
class _ListCommandOptions:
    print_as_table: Annotated[
        bool,
        typer.Option(
            "--table/--plain",
            help="Print list command as rich table",
            rich_help_panel="Printing Options",
        ),
    ] = True

    add_index: Annotated[
        bool,
        typer.Option(
            "--idx/--no-idx",
            help="Add index to the table",
            rich_help_panel="Printing Options",
        ),
    ] = True

    show_lines: Annotated[
        bool,
        typer.Option(
            "--lines/--no-lines",
            help="Add grid lines in the table",
            rich_help_panel="Printing Options",
        ),
    ] = True

    border_style: Annotated[
        TableBorderStyle,
        typer.Option(
            "--border-style",
            help="Table border style",
            rich_help_panel="Printing Options",
        ),
    ] = TableBorderStyle.ROUNDED


ListCommandOptionsDI = Annotated[_ListCommandOptions, Depends(_ListCommandOptions)]

ConsoleDI = Annotated[Console, Depends(lambda: Console(color_system="auto"))]
SessionDI = Annotated[Session, Depends(lambda: next(get_db()))]

HasherFnDI = Annotated[Callable[[str], str], Depends(lambda: hash_password)]
VerifierFnDI = Annotated[Callable[[str, str], bool], Depends(lambda: verify_password)]
