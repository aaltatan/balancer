from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from sqlalchemy.orm import Session

from app.db.user import UserDB
from app.utils.hash import hash_password, verify_password


class AuthenticationError(Exception):
    pass


def authenticate(db: Session, username: str, password: str) -> UserDB | None:
    user = db.query(UserDB).filter(UserDB.username == username).first()

    if user and not verify_password(password, user.hashed_password):
        return None

    return user


def change_user_password(db: Session, user: UserDB, old_password: str, new_password: str) -> UserDB:
    if not verify_password(old_password, user.hashed_password):
        message = f"Invalid password for user '{user.username}'."
        raise AuthenticationError(message)

    user.hashed_password = hash_password(new_password)
    db.commit()

    return user


def create_access_token(  # noqa: PLR0913
    data: dict[str, Any],
    expires_delta: int,
    expire_type: Literal["weeks", "days", "hours", "minutes"],
    token_type: Literal["access", "refresh"],
    secret_key: str,
    algorithm: str,
) -> str:
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(UTC) + timedelta(**{expire_type: expires_delta}),
            "token_type": token_type,
        }
    )
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_access_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(token, secret_key, algorithms=[algorithm])
