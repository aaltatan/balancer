import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import TIMESTAMP, UUID, Boolean, ColumnElement, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.timezone import get_default_tz_now

from ._association import users_permissions_association_table
from ._schema import Base

if TYPE_CHECKING:
    from .permission import PermissionDB
    from .tenant import TenantDB


type Role = Literal["superuser", "tenant-superuser", "tenant-user"]


class UserDB(Base):
    __tablename__ = "users"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(length=255), index=True)
    hashed_password: Mapped[str] = mapped_column(String(length=255))
    firstname: Mapped[str] = mapped_column(String(length=255))
    lastname: Mapped[str] = mapped_column(String(length=255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[Role] = mapped_column(String(length=255), default="tenant-user")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=get_default_tz_now)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, onupdate=get_default_tz_now, default=get_default_tz_now
    )

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.uid", ondelete="RESTRICT"), nullable=True
    )
    tenant: Mapped[Optional["TenantDB"]] = relationship(
        "TenantDB", back_populates="users", lazy="joined"
    )

    permissions: Mapped[set["PermissionDB"]] = relationship(
        "PermissionDB",
        secondary=users_permissions_association_table,
        back_populates="users",
        lazy="joined",
    )

    @hybrid_property
    def search(self) -> str:
        return (
            f"{self.username} {self.firstname} {self.lastname}"
            f"{self.username} {self.firstname} {self.lastname}"
        )

    @search.expression
    @classmethod
    def _search(cls) -> ColumnElement[str]:
        return (
            cls.username
            + " "
            + cls.firstname
            + " "
            + cls.lastname
            + " "
            + cls.username
            + " "
            + cls.firstname
            + " "
            + cls.lastname
        )

    @hybrid_property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"

    @fullname.expression
    @classmethod
    def _fullname(cls) -> ColumnElement[str]:
        return cls.firstname + " " + cls.lastname

    @hybrid_property
    def is_superuser(self) -> bool:
        return self.role == "superuser"

    @is_superuser.expression
    @classmethod
    def _is_superuser(cls) -> ColumnElement[bool]:
        return cls.role == "superuser"

    @hybrid_property
    def is_tenant_superuser(self) -> bool:
        return self.role == "tenant-superuser"

    @is_tenant_superuser.expression
    @classmethod
    def _is_tenant_superuser(cls) -> ColumnElement[bool]:
        return cls.role == "tenant-superuser"

    @hybrid_property
    def is_tenant_user(self) -> bool:
        return self.role == "tenant-user"

    @is_tenant_user.expression
    @classmethod
    def _is_tenant_user(cls) -> ColumnElement[bool]:
        return cls.role == "tenant-user"

    __table_args__ = (
        UniqueConstraint("username", "tenant_id", name="users_username_tenant_id_unique"),
    )

    def __repr__(self) -> str:
        return (
            "<UserDB("
            f"username={self.username}, "
            f"fullname={self.fullname}, "
            f"role={self.role}, "
            f"is_active={self.is_active}, "
            ")>"
        )
