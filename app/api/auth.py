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
from app.services.auth import (
    AuthenticationError,
    authenticate_superuser,
    authenticate_tenant_user,
    change_user_password,
    login,
)

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_authenticated_superuser(
    db: SessionDI, form: OAuth2Form, verifier_fn: PWDVerifierFnDI
) -> UserDB | None:
    return authenticate_superuser(db, form.username, form.password, verifier_fn)


def get_authenticated_tenant_user(
    db: SessionDI, form: OAuth2Form, tenant_db: ActiveTenantDI, verifier_fn: PWDVerifierFnDI
) -> UserDB | None:
    return authenticate_tenant_user(db, form.username, form.password, tenant_db, verifier_fn)


_SuperuserDI = Annotated[UserDB | None, Depends(get_authenticated_superuser)]
_TenantUserDI = Annotated[UserDB | None, Depends(get_authenticated_tenant_user)]


router = APIRouter()


@router.post("/superuser/token", response_model=AccessToken)
def login_superuser(config: ConfigDI, superuser: _SuperuserDI = None):
    try:
        return login(
            access_token_expires_in_minutes=config.jwt_access_token_expires_in_minutes,
            refresh_token_expires_in_days=config.jwt_refresh_token_expires_in_days,
            secret_key=config.jwt_secret_key,
            algorithm=config.jwt_algorithm,
            token_type=config.jwt_token_type,
            user=superuser,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{tenant_slug}/token", response_model=AccessToken)
def login_tenant_user(config: ConfigDI, tenant_user: _TenantUserDI = None):
    try:
        return login(
            access_token_expires_in_minutes=config.jwt_access_token_expires_in_minutes,
            refresh_token_expires_in_days=config.jwt_refresh_token_expires_in_days,
            secret_key=config.jwt_secret_key,
            algorithm=config.jwt_algorithm,
            token_type=config.jwt_token_type,
            user=tenant_user,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


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
            new_password=schema.new_password.get_secret_value(),
            verifier_fn=verifier_fn,
            hasher_fn=hasher_fn,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/me", response_model=UserReadWithoutRelations)
def get_user(user: ActiveUserDI):
    return user
