from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db import TenantDB, get_db


def get_current_tenant(
    db: Annotated[Session, Depends(get_db)], tenant_slug: Annotated[str, Path()]
) -> TenantDB:
    tenant = db.query(TenantDB).filter(TenantDB.slug == tenant_slug).first()

    if not tenant:
        message = f"Tenant with slug '{tenant_slug}' not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    if tenant.disabled:
        message = f"Tenant with slug '{tenant_slug}' is disabled."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    return tenant
