from balancer.config import get_config
from balancer.domain.models import init_db
from balancer.domain.models.permission import init_permissions
from balancer.entrypoint.cli.commands import api, superuser, tenant
from balancer.entrypoint.cli.dependencies import SessionDI
from typer_di import TyperDI


def callback(session: SessionDI) -> None:
    init_db()
    init_permissions(session)


def main() -> None:
    config = get_config()

    app = TyperDI(
        name=config.app_name, help=config.app_description, callback=callback, no_args_is_help=True
    )

    app.add_typer(api.app)

    app.add_typer(superuser.app, name="superuser")
    app.add_typer(tenant.app, name="tenant")

    app()


if __name__ == "__main__":
    main()
