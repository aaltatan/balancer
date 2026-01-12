from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.db.tenant import TenantDB
from app.exceptions import AlreadyExistsError, NotFoundError


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

    def get_by_slug(self, slug: str) -> TenantDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.slug == slug).first()

        if not tenant:
            message = f"Tenant with slug '{slug}' not found."
            raise NotFoundError(message)

        return tenant

    def create(self, schema: Schema) -> TenantDB:
        name = schema.model_dump().get("name", "")
        tenant_db_exists = self._db.query(TenantDB).filter(TenantDB.name == name).first()

        if tenant_db_exists:
            message = f"Tenant with uid '{name}' already exists."
            raise AlreadyExistsError(message)

        tenant_db = TenantDB(**schema.model_dump())

        self._db.add(tenant_db)
        self._db.commit()

        return tenant_db

    def update(self, slug: str, schema: Schema) -> TenantDB:
        tenant_db = self.get_by_slug(slug)

        for key, value in schema.model_dump().items():
            if value is not None:
                setattr(tenant_db, key, value)

        self._db.commit()
        self._db.refresh(tenant_db)

        return tenant_db

    def activate(self, slug: str) -> TenantDB:
        tenant_db = self.get_by_slug(slug)

        if not tenant_db.disabled:
            return tenant_db

        tenant_db.disabled = False
        self._db.commit()

        return tenant_db

    def deactivate(self, slug: str) -> TenantDB:
        tenant_db = self.get_by_slug(slug)

        if tenant_db.disabled:
            return tenant_db

        tenant_db.disabled = True
        self._db.commit()

        return tenant_db

    def delete(self, slug: str) -> None:
        tenant_db = self.get_by_slug(slug)
        self._db.delete(tenant_db)
        self._db.commit()
