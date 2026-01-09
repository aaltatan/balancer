# ruff: noqa: B008
from functools import partial
from typing import Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Config, get_config
from app.db import get_db
from app.db.tenant import TenantDB
from app.db.user import UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", refreshUrl="api/auth/token/refresh")


def _get_active_user(
    token_type: Literal["access", "refresh"],
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


get_active_user = partial(_get_active_user, "access")
get_active_user_refresh = partial(_get_active_user, "refresh")


def get_active_tenant(user: UserDB = Depends(get_active_user)) -> TenantDB:
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


def get_superuser(user: UserDB = Depends(get_active_user)) -> UserDB:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_tenant_superuser(user: UserDB = Depends(get_active_user)) -> UserDB:
    if not user.is_tenant_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
