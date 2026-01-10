from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import (
    ActiveUserDI,
    ActiveUserFromRefreshTokenDI,
    oauth2_scheme,
)
from app.api.dependencies.config import ConfigDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI, PWDVerifierFnDI
from app.models.auth import AccessToken, ChangePassword
from app.models.user import UserReadWithoutRelations
from app.services.auth import authenticate, change_user_password, create_access_token

router = APIRouter()


@router.post("/token", response_model=AccessToken)
def login(
    db: SessionDI,
    config: ConfigDI,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    verifier_fn: PWDVerifierFnDI,
):
    user = authenticate(db, form_data.username, form_data.password, verifier_fn)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {
        "sub": user.username,
        "tenant": user.tenant.slug if user.tenant else None,
        "role": user.role,
    }

    access_token = create_access_token(
        data=data,
        expires_delta=config.jwt_access_token_expires_in_minutes,
        expire_type="minutes",
        token_type="access",  # noqa: S106
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )

    refresh_token = create_access_token(
        data=data,
        expires_delta=config.jwt_refresh_token_expires_in_days,
        expire_type="days",
        token_type="refresh",  # noqa: S106
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh", response_model=AccessToken)
def get_access_token(
    config: ConfigDI,
    refresh_token: Annotated[str, Depends(oauth2_scheme)],
    user: ActiveUserFromRefreshTokenDI,
):
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=config.jwt_access_token_expires_in_minutes,
        expire_type="minutes",
        token_type="access",  # noqa: S106
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/me", response_model=UserReadWithoutRelations)
def get_user(user: ActiveUserDI):
    return user


@router.patch("/change-password", response_model=UserReadWithoutRelations)
def change_password(
    db: SessionDI,
    schema: Annotated[ChangePassword, Form()],
    user: ActiveUserDI,
    hasher_fn: PWDHasherFnDI,
    verifier_fn: PWDVerifierFnDI,
):
    return change_user_password(
        db=db,
        user=user,
        old_password=schema.old_password.get_secret_value(),
        new_password=schema.new_password.get_secret_value(),
        verifier_fn=verifier_fn,
        hasher_fn=hasher_fn,
    )
