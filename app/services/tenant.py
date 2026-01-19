from enum import StrEnum
from typing import Any, Literal, Protocol

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.tenant import TenantDB
from app.exceptions import AlreadyExistsError, CannotDeleteError, NotFoundError
from app.filters import get_criterion, get_order_by


class OrderBy(StrEnum):
    NAME_ASC = "name"
    NAME_DESC = "name (desc)"
    CODE = "code"
    CODE_DESC = "code (desc)"
    VALID_UNTIL_ASC = "valid until"
    VALID_UNTIL_DESC = "valid until (desc)"
    CREATED_AT_ASC = "created at"
    CREATED_AT_DESC = "created at (desc)"
    UPDATED_AT_ASC = "updated at"
    UPDATED_AT_DESC = "updated at (desc)"


ORDER_BY_FIELDS_MAPPER = {
    OrderBy.NAME_ASC: asc(TenantDB.name),
    OrderBy.NAME_DESC: desc(TenantDB.name),
    OrderBy.CODE: asc(TenantDB.code),
    OrderBy.CODE_DESC: desc(TenantDB.code),
    OrderBy.VALID_UNTIL_ASC: asc(TenantDB.valid_until),
    OrderBy.VALID_UNTIL_DESC: desc(TenantDB.valid_until),
    OrderBy.CREATED_AT_ASC: asc(TenantDB.created_at),
    OrderBy.CREATED_AT_DESC: desc(TenantDB.created_at),
    OrderBy.UPDATED_AT_ASC: asc(TenantDB.updated_at),
    OrderBy.UPDATED_AT_DESC: desc(TenantDB.updated_at),
}

FILTERS_FIELDS_MAPPER = {
    "search": TenantDB.search,
    "code": TenantDB.code,
    "phone": TenantDB.phone,
    "valid_until": TenantDB.valid_until,
}


class Schema(Protocol):
    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...


class Pagination(Protocol):
    page: int
    page_size: int

    @property
    def offset(self) -> int: ...

    @property
    def limit(self) -> int: ...


class TenantService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(
        self,
        order_by: list[OrderBy] | None = None,
        filter_schema: Schema | None = None,
        filtering_kind: Literal["and", "or"] = "and",
        pagination_schema: Pagination | None = None,
    ) -> tuple[list[TenantDB], int]:
        query = self._db.query(TenantDB)

        if order_by:
            query = query.order_by(*get_order_by(order_by, ORDER_BY_FIELDS_MAPPER))

        if filter_schema:
            query = query.filter(
                get_criterion(FILTERS_FIELDS_MAPPER, filter_schema, kind=filtering_kind)
            )

        count = query.count()

        if pagination_schema:
            query = query.offset(pagination_schema.offset).limit(pagination_schema.limit)

        return query.all(), count

    def get_by_code(self, code: str) -> TenantDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.code == code).first()

        if not tenant:
            message = f"Tenant with code '{code}' not found."
            raise NotFoundError(message)

        return tenant

    def create(self, schema: Schema) -> TenantDB:
        code = schema.model_dump()["code"]
        tenant_db_exists = self._db.query(TenantDB).filter(TenantDB.code == code).first()

        if tenant_db_exists:
            message = f"Tenant with uid '{code}' already exists."
            raise AlreadyExistsError(message)

        tenant_db = TenantDB(**schema.model_dump())

        self._db.add(tenant_db)
        self._db.commit()

        return tenant_db

    def update(self, code: str, schema: Schema) -> TenantDB:
        tenant_db = self.get_by_code(code)

        for key, value in schema.model_dump().items():
            if value is not None:
                setattr(tenant_db, key, value)

        self._db.commit()
        self._db.refresh(tenant_db)

        return tenant_db

    def activate(self, code: str) -> TenantDB:
        tenant_db = self.get_by_code(code)

        if not tenant_db.disabled:
            return tenant_db

        tenant_db.disabled = False
        self._db.commit()

        return tenant_db

    def deactivate(self, code: str) -> TenantDB:
        tenant_db = self.get_by_code(code)

        if tenant_db.disabled:
            return tenant_db

        tenant_db.disabled = True
        self._db.commit()

        return tenant_db

    def delete(self, code: str) -> None:
        tenant_db = self.get_by_code(code)

        if tenant_db.users:
            message = f"Cannot delete tenant with code '{code}' because it has users."
            raise CannotDeleteError(message)

        self._db.delete(tenant_db)
        self._db.commit()
