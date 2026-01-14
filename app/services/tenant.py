from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.db.tenant import TenantDB
from app.exceptions import AlreadyExistsError, NotFoundError, ObjectCannotBeDeletedError


class Schema(Protocol):
    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...


class TenantService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(self) -> list[TenantDB]:
        return self._db.query(TenantDB).all()

    def get_by_uid(self, uid: str) -> TenantDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.uid == uid).first()

        if not tenant:
            message = f"Tenant with uid '{uid}' not found."
            raise NotFoundError(message)

        return tenant

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
            raise ObjectCannotBeDeletedError(message)

        self._db.delete(tenant_db)
        self._db.commit()
