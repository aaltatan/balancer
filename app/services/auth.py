# ruff: noqa: PLR0913, S106
from typing import TypedDict

from sqlalchemy.orm import Session

from app.db.user import UserDB
from app.exceptions import AuthenticationError
from app.utils.security import PWDHasherFn, PWDVerifierFn, create_access_token


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
) -> AccessToken:
    data = {"sub": user.username, "role": user.role}

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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_type,
    }


def change_user_password(
    db: Session,
    user: UserDB,
    old_password: str,
    new_password: str,
    verifier_fn: PWDVerifierFn,
    hasher_fn: PWDHasherFn,
) -> UserDB:
    if not verifier_fn(old_password, user.hashed_password):
        message = f"Invalid password for user '{user.username}'."
        raise AuthenticationError(message)

    user.hashed_password = hasher_fn(new_password)
    db.commit()

    return user
