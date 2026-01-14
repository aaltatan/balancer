from rich.table import Table

from app.db.tenant import TenantDB


def get_table(tenants: list[TenantDB]) -> Table:
    table = Table(title="Tenants")
    table.add_column("Code", justify="left", no_wrap=True)
    table.add_column("Name", justify="left", no_wrap=True)
    table.add_column("Valid Until", justify="left", no_wrap=True)
    table.add_column("Users", justify="left", no_wrap=True)
    table.add_column("Is Active", justify="left", no_wrap=True)

    for tenant in tenants:
        table.add_row(
            tenant.code,
            tenant.name,
            tenant.valid_until.strftime("%Y-%m-%d"),
            str(len(tenant.users)),
            "Yes" if not tenant.disabled else "No",
        )

    return table
