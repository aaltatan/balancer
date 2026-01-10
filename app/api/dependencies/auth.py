from collections.abc import Callable
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Config
from app.db.user import UserDB

from .config import ConfigDI
from .db import SessionDI

oauth2_scheme_superuser = OAuth2PasswordBearer(
    scheme_name="superuser", tokenUrl="/api/auth/superuser/token"
)
oauth2_scheme_tenant = OAuth2PasswordBearer(
    scheme_name="tenant", tokenUrl="/api/auth/{tenant_slug}/token"
)

type _WrapperFn = Callable[[Session, Config, str], UserDB]


def get_active_user(
    token_type: Literal["access", "refresh"],
    scheme: OAuth2PasswordBearer,
    *,
    is_superuser: bool = False,
) -> _WrapperFn:
    def wrapper(db: SessionDI, config: ConfigDI, token: Annotated[str, Depends(scheme)]) -> UserDB:
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

        query = db.query(UserDB).filter(UserDB.username == username)

        if is_superuser:
            query = query.filter(UserDB.is_superuser)

        user = query.first()

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


def get_tenant_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_tenant_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


ActiveUserDI = Annotated[UserDB, Depends(get_active_user("access", oauth2_scheme_tenant))]
TenantSuperuserDI = Annotated[UserDB, Depends(get_tenant_superuser)]
SuperuserDI = Annotated[UserDB, Depends(get_active_user("access", oauth2_scheme_superuser))]

RequireActiveUserDI = Depends(get_active_user("access", oauth2_scheme_tenant))
RequireTenantSuperuserDI = Depends(get_tenant_superuser)
RequireSuperuserDI = Depends(get_active_user("access", oauth2_scheme_superuser))
