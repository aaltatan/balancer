from sqlalchemy import Column, ForeignKey, Table

from ._schema import Base

users_permissions_association_table = Table(
    "users_permissions_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.uid"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.uid"), primary_key=True),
)
