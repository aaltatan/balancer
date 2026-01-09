from sqlalchemy.orm import Session

from app.db import UserDB
from app.utils.hash import hash_password

from .user import UserAlreadyExistsError


class AdminService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def create_superuser(
        self, username: str, firstname: str, lastname: str, password: str
    ) -> UserDB:
        user_db_exists = self._db.query(UserDB).filter(UserDB.username == username).first()

        if user_db_exists:
            message = f"User with username '{username}' already exists."
            raise UserAlreadyExistsError(message)

        user_db = UserDB(
            username=username,
            firstname=firstname,
            lastname=lastname,
            role="superuser",
            hashed_password=hash_password(password),
        )

        self._db.add(user_db)
        self._db.commit()
        self._db.refresh(user_db)

        return user_db
