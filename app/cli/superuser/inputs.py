from typing import Annotated

import typer

UsernameOpt = Annotated[str, typer.Option("--username", "-u")]
FirstnameOpt = Annotated[str, typer.Option("--firstname", "-f")]
LastnameOpt = Annotated[str, typer.Option("--lastname", "-l")]
PasswordOpt = Annotated[
    str, typer.Option("--password", prompt="Password", hide_input=True, confirmation_prompt=True)
]
