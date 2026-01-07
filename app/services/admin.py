from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.db import UserDB
from app.utils.hash import hash_password

from .user import UserAlreadyExistsError


class CreateSchema(Protocol):
    username: str
    firstname: str
    lastname: str

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...


class AdminService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def create_superuser(self, user: CreateSchema, password: str) -> UserDB:
        user_db_exists = self._db.query(UserDB).filter(UserDB.username == user.username).first()

        if user_db_exists:
            message = f"User with username '{user.username}' already exists."
            raise UserAlreadyExistsError(message)

        user_db = UserDB(
            **user.model_dump(), role="superuser", hashed_password=hash_password(password)
        )

        self._db.add(user_db)
        self._db.commit()
        self._db.refresh(user_db)

        return user_db
