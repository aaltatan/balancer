from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_active_user, get_active_user_refresh, oauth2_scheme
from app.core.config import Config, get_config
from app.db import get_db
from app.db.user import UserDB
from app.models.auth import AccessToken, ChangePassword
from app.models.user import UserReadWithoutRelations
from app.services.auth import authenticate, change_user_password, create_access_token

router = APIRouter()


@router.post("/token", response_model=AccessToken)
def login(
    db: Annotated[Session, Depends(get_db)],
    config: Annotated[Config, Depends(get_config)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=config.jwt_access_token_expires_in_minutes,
        expire_type="minutes",
        token_type="access",  # noqa: S106
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )

    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=config.jwt_refresh_token_expires_in_days,
        expire_type="days",
        token_type="refresh",  # noqa: S106
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh", response_model=AccessToken)
def get_access_token(
    config: Annotated[Config, Depends(get_config)],
    refresh_token: Annotated[str, Depends(oauth2_scheme)],
    user: Annotated[UserDB, Depends(get_active_user_refresh)],
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
def get_user(user: Annotated[UserDB, Depends(get_active_user)]):
    return user


@router.patch(
    "/change-password",
    response_model=UserReadWithoutRelations,
    dependencies=[Depends(get_active_user)],
)
def change_password(
    db: Annotated[Session, Depends(get_db)],
    schema: Annotated[ChangePassword, Form()],
    user: Annotated[UserDB, Depends(get_active_user)],
):
    return change_user_password(
        db, user, schema.old_password.get_secret_value(), schema.new_password.get_secret_value()
    )
