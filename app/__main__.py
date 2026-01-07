# ruff: noqa: PLC0415
import sys
from pathlib import Path

import typer


def main() -> None:
    sys.path.append(str(Path(__file__).parent.parent))

    from app.cli.users.cli import app as users_app
    from app.core.config import get_config
    from app.db import SessionLocal, init_db
    from app.db.permission import init_permissions

    with SessionLocal() as session:
        init_db()
        init_permissions(session)

    config = get_config()

    app = typer.Typer(name=config.app_name, help=config.app_description)
    app.add_typer(users_app, name="users")

    app()


if __name__ == "__main__":
    main()
