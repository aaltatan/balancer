# ruff: noqa: PLR0913, S106
from collections.abc import Callable
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from balancer.domain.exceptions import AuthenticationError
from balancer.domain.models.tenant import TenantDB
from balancer.domain.models.user import UserDB
from balancer.utils.security import create_access_token


class AccessToken(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str


def get_tokens(
    user: UserDB,
    access_token_expires_in_minutes: int,
    refresh_token_expires_in_days: int,
    secret_key: str,
    algorithm: str,
    token_type: str,
    tenant_db: TenantDB | None = None,
) -> AccessToken:
    data: dict[str, Any] = {"sub": user.username, "role": user.role}

    if tenant_db:
        data["tenant"] = {"uid": tenant_db.uid.hex, "name": tenant_db.name}
    else:
        data["tenant"] = None

    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires_in_minutes,
        expire_type="minutes",
        token_type="access",
        secret_key=secret_key,
        algorithm=algorithm,
    )

    refresh_token = create_access_token(
        data=data,
        expires_delta=refresh_token_expires_in_days,
        expire_type="days",
        token_type="refresh",
        secret_key=secret_key,
        algorithm=algorithm,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": token_type}


def change_user_password(
    db: Session,
    user: UserDB,
    old_password: str,
    new_hashed_password: str,
    verifier_fn: Callable[[str, str], bool],
) -> UserDB:
    if not verifier_fn(old_password, user.hashed_password):
        message = f"Invalid password for user '{user.username}'."
        raise AuthenticationError(message)

    user.hashed_password = new_hashed_password
    db.commit()

    return user
