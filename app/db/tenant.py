import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import (
    DATE,
    TIMESTAMP,
    UUID,
    Boolean,
    ColumnElement,
    Connection,
    String,
    event,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship

from ._schema import Base

if TYPE_CHECKING:
    from .user import UserDB


class TenantDB(Base):
    __tablename__ = "tenants"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    valid_from: Mapped[datetime] = mapped_column(DATE)
    valid_to: Mapped[datetime] = mapped_column(DATE)

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, onupdate=func.now(), default=func.now())

    users: Mapped[set["UserDB"]] = relationship("UserDB", back_populates="tenant", lazy="joined")

    @hybrid_property
    def is_active(self) -> bool:
        return (
            self.valid_from <= datetime.now(tz=timezone.utc) <= self.valid_to
        ) or not self.disabled

    @is_active.expression
    @classmethod
    def _is_active(cls) -> ColumnElement[bool]:
        return (cls.valid_from <= func.now(timezone=True) <= cls.valid_to) or cls.disabled != True  # noqa: E712

    def __repr__(self) -> str:
        return f"<TenantDB(name={self.name})>"


def set_tenant_slugify(mapper: Mapper, connection: Connection, target: TenantDB) -> None:  # noqa: ARG001
    if target.name:
        target.slug = slugify(target.name, allow_unicode=True)


event.listen(TenantDB, "before_insert", set_tenant_slugify)
event.listen(TenantDB, "before_insert", set_tenant_slugify)
