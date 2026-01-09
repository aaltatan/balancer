from rich.table import Table

from app.db.user import UserDB


def get_table(users: list[UserDB]) -> Table:
    table = Table(title="Users")
    table.add_column("Created At", justify="left", no_wrap=True)
    table.add_column("Updated At", justify="left", no_wrap=True)
    table.add_column("Username", justify="left", no_wrap=True)
    table.add_column("Fullname", justify="left", no_wrap=True)
    table.add_column("Role", justify="left", no_wrap=True)
    table.add_column("Is Active", justify="left", no_wrap=True)

    for user in users:
        table.add_row(
            user.created_at.strftime("%Y-%m-%d"),
            user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            user.username,
            user.fullname,
            user.role,
            "Yes" if user.is_active else "No",
        )

    return table
