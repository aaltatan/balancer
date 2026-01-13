from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import ActiveUserDI
from app.api.dependencies.config import ConfigDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI, PWDVerifierFnDI
from app.api.dependencies.tenant import ActiveTenantDI
from app.db.user import UserDB
from app.models.auth import AccessToken, ChangePassword
from app.models.user import UserReadWithoutRelations
from app.services.auth import AuthenticationError, change_user_password, get_tokens

router = APIRouter()


@router.post("/superuser/token", response_model=AccessToken)
def login_superuser(
    config: ConfigDI,
    session: SessionDI,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    superuser = (
        session.query(UserDB)
        .filter(UserDB.username == form_data.username, UserDB.is_superuser)
        .first()
    )

    if not superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not superuser.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    return get_tokens(
        access_token_expires_in_minutes=config.jwt_access_token_expires_in_minutes,
        refresh_token_expires_in_days=config.jwt_refresh_token_expires_in_days,
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
        token_type=config.jwt_token_type,
        user=superuser,
    )


@router.post("/{tenant_code}/token", response_model=AccessToken)
def login_tenant_user(
    config: ConfigDI,
    session: SessionDI,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    tenant_db: ActiveTenantDI,
):
    tenant_user = (
        session.query(UserDB)
        .filter(UserDB.username == form_data.username, UserDB.tenant == tenant_db)
        .first()
    )

    if not tenant_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not tenant_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    if tenant_user.tenant and not tenant_user.tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant is not active")

    return get_tokens(
        user=tenant_user,
        access_token_expires_in_minutes=config.jwt_access_token_expires_in_minutes,
        refresh_token_expires_in_days=config.jwt_refresh_token_expires_in_days,
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
        token_type=config.jwt_token_type,
        tenant_db=tenant_user.tenant,
    )


@router.patch("/change-password", response_model=UserReadWithoutRelations)
def change_password(
    db: SessionDI,
    schema: Annotated[ChangePassword, Form()],
    user: ActiveUserDI,
    verifier_fn: PWDVerifierFnDI,
    hasher_fn: PWDHasherFnDI,
):
    try:
        return change_user_password(
            db=db,
            user=user,
            old_password=schema.old_password.get_secret_value(),
            new_hashed_password=hasher_fn(schema.new_password.get_secret_value()),
            verifier_fn=verifier_fn,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/me", response_model=UserReadWithoutRelations)
def get_user(user: ActiveUserDI):
    return user
