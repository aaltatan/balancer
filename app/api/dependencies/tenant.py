from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from pydantic import AfterValidator

from app.db.tenant import TenantDB
from app.db.user import UserDB
from app.schemas.tenant import validate_code

from .auth import get_active_user
from .utils import SessionDI


def get_active_tenant_from_token(user: Annotated[UserDB, Depends(get_active_user)]) -> TenantDB:
    if user.tenant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user.tenant


def get_active_tenant_from_path(
    db: SessionDI,
    code: Annotated[
        str, Path(min_length=4, max_length=4, examples=["dbgh"]), AfterValidator(validate_code)
    ],
) -> TenantDB:
    tenant_db = db.query(TenantDB).filter(TenantDB.code == code).first()

    if not tenant_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not tenant_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tenant_db


TenantDBFromPathDI = Annotated[TenantDB, Depends(get_active_tenant_from_path)]
TenantDBFromTokenDI = Annotated[TenantDB, Depends(get_active_tenant_from_token)]
