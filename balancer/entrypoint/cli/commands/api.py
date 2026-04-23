from dataclasses import dataclass
from typing import Annotated

import typer
import uvicorn
from typer_di import Depends, TyperDI


@dataclass
class _ServerOptions:
    app: Annotated[str, typer.Option("--app", "-a")] = "balancer.entrypoint.api.main:app"
    reload: Annotated[bool, typer.Option("--reload", "-r", envvar="DEBUG")] = True
    host: Annotated[str, typer.Option("--host", "-h", envvar="HOST")] = "127.0.0.1"
    port: Annotated[int, typer.Option("--port", "-p", envvar="PORT")] = 8000


app = TyperDI()


@app.command(name="api")
def run_server(options: Annotated[_ServerOptions, Depends(_ServerOptions)]) -> None:
    """Run the API server."""
    uvicorn.run(options.app, host=options.host, port=options.port, reload=options.reload)
