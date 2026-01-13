import uuid
from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import Config
from app.db.tenant import TenantDB
from app.db.user import UserDB

from .config import ConfigDI
from .db import SessionDI

oauth2_scheme_superuser = OAuth2PasswordBearer(
    scheme_name="superuser", tokenUrl="/api/auth/superuser/token"
)
oauth2_scheme_tenant = OAuth2PasswordBearer(
    scheme_name="tenant", tokenUrl="/api/auth/{tenant_code}/token"
)


def get_active_user(scheme: OAuth2PasswordBearer) -> Callable[[Session, Config, str], UserDB]:
    def wrapper(db: SessionDI, config: ConfigDI, token: Annotated[str, Depends(scheme)]) -> UserDB:
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
                db.query(TenantDB)
                .filter(TenantDB.uid == uuid.UUID(payload["tenant"]["uid"]))
                .first()
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

        if scheme.scheme_name == "superuser":
            query = query.filter(UserDB.is_superuser)

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

    return wrapper


def get_tenant_superuser(user: "ActiveUserDI") -> UserDB:
    if not user.is_tenant_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superuser privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


RequireActiveUserDI = Depends(get_active_user(oauth2_scheme_tenant))
RequireTenantSuperuserDI = Depends(get_tenant_superuser)
RequireSuperuserDI = Depends(get_active_user(oauth2_scheme_superuser))

ActiveUserDI = Annotated[UserDB, RequireActiveUserDI]
TenantSuperuserDI = Annotated[UserDB, RequireTenantSuperuserDI]
SuperuserDI = Annotated[UserDB, RequireSuperuserDI]
