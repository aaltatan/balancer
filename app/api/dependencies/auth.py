# ruff: noqa: B008
from collections.abc import Callable
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Config, get_config
from app.db import get_db
from app.db.tenant import TenantDB
from app.db.user import UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", refreshUrl="api/auth/token/refresh")

type _WrapperFn = Callable[[Session, str, Config], UserDB]


def get_active_user(token_type: Literal["access", "refresh"]) -> _WrapperFn:
    def wrapper(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
        config: Config = Depends(get_config),
    ) -> UserDB:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        except jwt.InvalidTokenError:
            raise exception from None

        if payload.get("token_type") != token_type:
            raise exception

        username = payload.get("sub")

        if not username:
            raise exception

        user = db.query(UserDB).filter(UserDB.username == username).first()

        if not user:
            raise exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    return wrapper


def get_active_tenant(user: "ActiveUserDI") -> TenantDB:
    if not user.tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user.tenant


def get_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_tenant_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_tenant_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


ActiveUserDI = Annotated[UserDB, Depends(get_active_user("access"))]
ActiveUserFromRefreshTokenDI = Annotated[UserDB, Depends(get_active_user("refresh"))]
ActiveTenantDI = Annotated[TenantDB, Depends(get_active_tenant)]
TenantSuperuserDI = Annotated[UserDB, Depends(get_tenant_superuser)]
SuperuserDI = Annotated[UserDB, Depends(get_superuser)]

RequireActiveUserDI = Depends(get_active_user("access"))
RequireActiveUserFromRefreshTokenDI = Depends(get_active_user("refresh"))
RequireActiveTenantDI = Depends(get_active_tenant)
RequireTenantSuperuserDI = Depends(get_tenant_superuser)
RequireSuperuserDI = Depends(get_superuser)
