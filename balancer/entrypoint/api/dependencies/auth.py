import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from balancer.domain.models.tenant import TenantDB
from balancer.domain.models.user import UserDB

from .config import ConfigDI
from .db import SessionDI

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def _get_active_user(
    db: SessionDI, config: ConfigDI, token: Annotated[str, Depends(oauth2_scheme)]
) -> UserDB:
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
    except jwt.InvalidTokenError:
        raise invalid_credentials_exc from None

    username = payload.get("sub")

    if not username:
        raise invalid_credentials_exc

    query = db.query(UserDB).filter(UserDB.username == username)

    if payload.get("tenant"):
        tenant_db = (
            db.query(TenantDB).filter(TenantDB.uid == uuid.UUID(payload["tenant"]["uid"])).first()
        )

        if not tenant_db:
            raise invalid_credentials_exc

        if not tenant_db.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )

        query = query.filter(UserDB.tenant == tenant_db)
    else:
        query = query.filter(UserDB.tenant == None)  # noqa: E711

    user = query.first()

    if not user:
        raise invalid_credentials_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


RequireActiveUserDI = Depends(_get_active_user)
ActiveUserDI = Annotated[UserDB, RequireActiveUserDI]


def _get_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


RequireSuperuserDI = Depends(_get_superuser)
SuperuserDI = Annotated[UserDB, RequireSuperuserDI]


def _get_tenant_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_tenant_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


RequireTenantSuperuserDI = Depends(_get_tenant_superuser)
TenantSuperuserDI = Annotated[UserDB, RequireTenantSuperuserDI]


def _get_any_superuser(user: "ActiveUserDI") -> UserDB:
    if user.role not in ["superuser", "tenant-superuser"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


RequireAnySuperuserDI = Depends(_get_any_superuser)
AnySuperuserDI = Annotated[UserDB, RequireAnySuperuserDI]
