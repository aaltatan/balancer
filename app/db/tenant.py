import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DATE, TIMESTAMP, UUID, Boolean, ColumnElement, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.timezone import get_default_tz_now

from ._schema import Base

if TYPE_CHECKING:
    from .user import UserDB


class TenantDB(Base):
    __tablename__ = "tenants"

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    valid_until: Mapped[datetime] = mapped_column(DATE)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    address: Mapped[str] = mapped_column(String(255), default="")
    city: Mapped[str] = mapped_column(String(255), default="")
    country: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(String(255), default="")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=get_default_tz_now)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, onupdate=get_default_tz_now, default=get_default_tz_now
    )

    users: Mapped[set["UserDB"]] = relationship("UserDB", back_populates="tenant", lazy="joined")

    @hybrid_property
    def search(self) -> str:  # pyright: ignore[reportRedeclaration]
        return f"{self.name} {self.code} {self.name}"

    @search.inplace.expression
    @classmethod
    def search(cls) -> ColumnElement[str]:
        return func.concat(cls.name, " ", cls.code, " ", cls.name)

    @hybrid_property
    def is_outdated(self) -> bool:
        now = datetime.now(tz=timezone.utc).date()
        return now > self.valid_until

    @is_outdated.inplace.expression
    @classmethod
    def _is_outdated(cls) -> ColumnElement[bool]:
        return func.current_date() <= cls.valid_until

    @hybrid_property
    def is_active(self) -> bool:
        return not self.is_outdated and not self.disabled

    @is_active.inplace.expression
    @classmethod
    def _is_active(cls) -> ColumnElement[bool]:
        return ~cls._is_outdated & ~cls.disabled

    def __repr__(self) -> str:
        return (
            "<TenantDB("
            f"name={self.name}, "
            f"code={self.code}, "
            f"is_outdated={self.is_outdated}, "
            f"disabled={self.disabled}, "
            f"is_active={self.is_active}, "
            f"valid_until={self.valid_until}"
            ")>"
        )
