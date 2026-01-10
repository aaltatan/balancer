from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from app.db.tenant import TenantDB

from .db import SessionDI


def get_active_tenant(db: SessionDI, tenant_slug: Annotated[str, Path()]) -> TenantDB:
    tenant = db.query(TenantDB).filter(TenantDB.slug == tenant_slug).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tenant


ActiveTenantDI = Annotated[TenantDB, Depends(get_active_tenant)]
