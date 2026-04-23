import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Enum
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from ._association import users_permissions_association_table
from ._schema import Base

if TYPE_CHECKING:
    from .user import UserDB


class Permission(StrEnum):
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_CREATE = "users:create"
    USERS_EXPORT = "users:export"

    def __str__(self) -> str:
        return self.value


def init_permissions(session: Session) -> None:
    existing_db_permissions = session.scalars(session.query(PermissionDB.name)).all()
    permissions_db = [
        PermissionDB(name=perm) for perm in Permission if perm not in existing_db_permissions
    ]
    session.add_all(permissions_db)
    session.commit()


class PermissionDB(Base):
    __tablename__ = "permissions"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[Permission] = mapped_column(Enum(Permission), unique=True, index=True)

    users: Mapped[set["UserDB"]] = relationship(
        "UserDB",
        secondary=users_permissions_association_table,
        back_populates="permissions",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<PermissionDB(name={self.name})>"
