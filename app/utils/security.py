from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


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
