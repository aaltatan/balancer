from typing import Annotated

import typer

UsernameArg = Annotated[str, typer.Argument()]
UsernameOpt = Annotated[str, typer.Option("--username", "-u")]
FirstnameOpt = Annotated[str, typer.Option("--firstname", "-f")]
OptionalFirstnameOpt = Annotated[str | None, typer.Option("--firstname", "-f")]
LastnameOpt = Annotated[str, typer.Option("--lastname", "-l")]
OptionalLastnameOpt = Annotated[str | None, typer.Option("--lastname", "-l")]
PasswordOpt = Annotated[
    str, typer.Option("--password", prompt="Password", hide_input=True, confirmation_prompt=True)
]
