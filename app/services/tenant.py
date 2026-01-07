from sqlalchemy.orm import Session

from app.db.tenant import TenantDB
from app.models.tenant import TenantCreate, TenantUpdate


class TenantNotFoundError(Exception):
    pass


class TenantAlreadyExistsError(Exception):
    pass


class TenantService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(self) -> list[TenantDB]:
        return self._db.query(TenantDB).all()

    def get_by_uid(self, uid: str) -> TenantDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.uid == uid).first()

        if not tenant:
            message = f"Tenant with uid '{uid}' not found."
            raise TenantNotFoundError(message)

        return tenant

    def get_by_slug(self, slug: str) -> TenantDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.slug == slug).first()

        if not tenant:
            message = f"Tenant with slug '{slug}' not found."
            raise TenantNotFoundError(message)

        return tenant

    def create(self, tenant: TenantCreate) -> TenantDB:
        tenant_db_exists = self._db.query(TenantDB).filter(TenantDB.name == tenant.name).first()

        if tenant_db_exists:
            message = f"Tenant with uid '{tenant.name}' already exists."
            raise TenantAlreadyExistsError(message)

        tenant_db = TenantDB(**tenant.model_dump())

        self._db.add(tenant_db)
        self._db.commit()
        self._db.refresh(tenant_db)

        return tenant_db

    def update(self, slug: str, tenant: TenantUpdate) -> TenantDB:
        tenant_db = self.get_by_slug(slug)

        for key, value in tenant.model_dump().items():
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
        self._db.refresh(tenant_db)

        return tenant_db

    def deactivate(self, slug: str) -> TenantDB:
        tenant_db = self.get_by_slug(slug)

        if tenant_db.disabled:
            return tenant_db

        tenant_db.disabled = True
        self._db.commit()
        self._db.refresh(tenant_db)

        return tenant_db

    def delete(self, slug: str) -> None:
        tenant_db = self.get_by_slug(slug)
        self._db.delete(tenant_db)
        self._db.commit()
