from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from app.db.tenant import TenantDB

from .auth import ActiveUserDI
from .db import SessionDI


def get_active_tenant(
    db: SessionDI,
    user: ActiveUserDI,
    tenant_code: Annotated[str, Path()],
) -> TenantDB:
    tenant = db.query(TenantDB).filter(TenantDB.code == tenant_code).first()

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

    if not user.is_superuser:
        user_belong_to_tenant = (
            db.query(TenantDB)
            .filter(TenantDB.users.contains(user), TenantDB.code == tenant.code)
            .first()
        )

        if not user_belong_to_tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"'{tenant.code}' privileges required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return tenant


ActiveTenantDI = Annotated[TenantDB, Depends(get_active_tenant)]
