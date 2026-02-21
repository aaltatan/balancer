import re
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import ActiveUserDI
from app.api.dependencies.utils import ConfigDI, PWDHasherFnDI, PWDVerifierFnDI, SessionDI
from app.constants import LOGIN_USERNAME_REGEX
from app.db.tenant import TenantDB
from app.db.user import UserDB
from app.schemas.auth import AccessTokenSchema, ChangePasswordSchema
from app.schemas.user import UserReadWithTenant
from app.services.auth import change_user_password, get_tokens

router = APIRouter()


def parse_username_tenant(username: str, pattern: str) -> tuple[str, str | None]:
    tenant_code: str | None = None

    if re.match(pattern, username) and "@" in username:
        username, tenant_code = username.split("@")

    return username, tenant_code


def forbidden_exc(kind: Literal["tenant", "user"]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"{kind.title()} is not active",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/token", response_model=AccessTokenSchema)
def login_superuser(
    config: ConfigDI,
    session: SessionDI,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )

    username, tenant_code = parse_username_tenant(form_data.username, LOGIN_USERNAME_REGEX)
    tenant: TenantDB | None = None

    if tenant_code:
        tenant = session.query(TenantDB).filter(TenantDB.code == tenant_code).first()

        if not tenant:
            raise invalid_credentials_exc

        if not tenant.is_active:
            raise forbidden_exc(kind="tenant")

    user = (
        session.query(UserDB).filter(UserDB.username == username, UserDB.tenant == tenant).first()
    )

    if not user:
        raise invalid_credentials_exc

    if not user.is_active:
        raise forbidden_exc(kind="user")

    return get_tokens(
        access_token_expires_in_minutes=config.jwt_access_token_expires_in_minutes,
        refresh_token_expires_in_days=config.jwt_refresh_token_expires_in_days,
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm,
        token_type=config.jwt_token_type,
        user=user,
        tenant_db=tenant,
    )


@router.patch("/change-password", response_model=UserReadWithTenant)
def change_password(
    db: SessionDI,
    schema: Annotated[ChangePasswordSchema, Form()],
    user: ActiveUserDI,
    verifier_fn: PWDVerifierFnDI,
    hasher_fn: PWDHasherFnDI,
):
    return change_user_password(
        db=db,
        user=user,
        old_password=schema.old_password.get_secret_value(),
        new_hashed_password=hasher_fn(schema.new_password.get_secret_value()),
        verifier_fn=verifier_fn,
    )


@router.post("/me", response_model=UserReadWithTenant)
def get_user(user: ActiveUserDI):
    return user
