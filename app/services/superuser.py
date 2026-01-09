from sqlalchemy.orm import Session

from app.db import UserDB

from .generic_user import GenericUserService, MoreThanOneSuperuserError, UserNotFoundError


class SuperuserService:
    def __init__(self, session: Session, service: GenericUserService) -> None:
        self._db = session
        self._service = service

    def _get_superuser(self) -> UserDB:
        query = self._db.query(UserDB).filter(UserDB.role == "superuser")

        user = query.first()

        if not user:
            message = "No superuser found."
            raise UserNotFoundError(message)

        return user

    def create(self, username: str, firstname: str, lastname: str, plain_password: str) -> UserDB:
        if self._db.query(UserDB).filter(UserDB.is_superuser).count() >= 1:
            message = "More than one superuser is not allowed."
            raise MoreThanOneSuperuserError(message)

        return self._service.create(username, firstname, lastname, plain_password, role="superuser")

    def reset_password(self, new_password: str) -> UserDB:
        superuser = self._get_superuser()
        return self._service.reset_password(superuser, new_password)
