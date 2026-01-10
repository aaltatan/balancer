from collections.abc import Callable
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import Config
from app.db.user import UserDB

from .config import ConfigDI
from .db import SessionDI
from .hash import PWDVerifierFnDI
from .tenant import ActiveTenantDI

oauth2_scheme_superuser = OAuth2PasswordBearer(
    scheme_name="superuser", tokenUrl="/api/auth/superuser/token"
)
oauth2_scheme_tenant = OAuth2PasswordBearer(
    scheme_name="tenant", tokenUrl="/api/auth/{tenant_slug}/token"
)

type _WrapperFn = Callable[[Session, Config, str], UserDB]

_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_active_user(
    token_type: Literal["access", "refresh"],
    scheme: OAuth2PasswordBearer,
    *,
    is_superuser: bool = False,
) -> _WrapperFn:
    def wrapper(db: SessionDI, config: ConfigDI, token: Annotated[str, Depends(scheme)]) -> UserDB:
        exception_401_unauthorized = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        except jwt.InvalidTokenError:
            raise exception_401_unauthorized from None

        if payload.get("token_type") != token_type:
            raise exception_401_unauthorized

        username = payload.get("sub")

        if not username:
            raise exception_401_unauthorized

        query = db.query(UserDB).filter(UserDB.username == username)

        if is_superuser:
            query = query.filter(UserDB.is_superuser)

        user = query.first()

        if not user:
            raise exception_401_unauthorized

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


def get_authenticated_superuser(
    db: SessionDI, form: _OAuth2Form, verifier_fn: PWDVerifierFnDI
) -> UserDB:
    superuser = (
        db.query(UserDB).filter(UserDB.username == form.username, UserDB.is_superuser).first()
    )

    if not superuser or not verifier_fn(form.password, superuser.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not superuser.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    return superuser


def get_authenticated_tenant_user(
    db: SessionDI, form: _OAuth2Form, tenant_db: ActiveTenantDI, verifier_fn: PWDVerifierFnDI
) -> UserDB:
    user = (
        db.query(UserDB)
        .filter(UserDB.username == form.username, UserDB.tenant == tenant_db, ~UserDB.is_superuser)
        .first()
    )

    if not user or not verifier_fn(form.password, user.hashed_password) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    if not user.tenant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not tenant user")

    if not user.tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is not active")

    return user


AuthenticatedSuperuserDI = Annotated[UserDB, Depends(get_authenticated_superuser)]
AuthenticatedTenantUserDI = Annotated[UserDB, Depends(get_authenticated_tenant_user)]

RequireActiveUserDI = Depends(get_active_user("access", oauth2_scheme_tenant))
RequireTenantSuperuserDI = Depends(get_tenant_superuser)
RequireSuperuserDI = Depends(get_active_user("access", oauth2_scheme_superuser, is_superuser=True))

ActiveUserDI = Annotated[UserDB, RequireActiveUserDI]
TenantSuperuserDI = Annotated[UserDB, RequireTenantSuperuserDI]
SuperuserDI = Annotated[UserDB, RequireSuperuserDI]
