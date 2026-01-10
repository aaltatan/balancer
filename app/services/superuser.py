from sqlalchemy.orm import Session

from app.db import UserDB
<<<<<<< HEAD
from app.utils.hash import PWDHasherFn
=======
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225

from .generic_user import GenericUserService, UserNotFoundError


class SuperuserService:
    def __init__(self, session: Session, service: GenericUserService) -> None:
        self._db = session
        self._service = service

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).filter(UserDB.role == "superuser").all()

    def _get_superuser(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(UserDB.role == "superuser", UserDB.username == username)
            .first()
        )

        if not user:
            message = f"User with username '{username}' not found."
            raise UserNotFoundError(message)

        return user

<<<<<<< HEAD
    def create(
        self,
        username: str,
        firstname: str,
        lastname: str,
        plain_password: str,
        hasher_fn: PWDHasherFn,
    ) -> UserDB:
        return self._service.create(
            username, firstname, lastname, plain_password, role="superuser", hasher_fn=hasher_fn
        )
=======
    def create(self, username: str, firstname: str, lastname: str, plain_password: str) -> UserDB:
        return self._service.create(username, firstname, lastname, plain_password, role="superuser")
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225

    def update(
        self, username: str, firstname: str | None = None, lastname: str | None = None
    ) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.update(superuser, firstname, lastname)

    def activate(self, username: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.activate(superuser)

    def deactivate(self, username: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.deactivate(superuser)

    def delete(self, username: str) -> None:
        superuser = self._get_superuser(username)
        return self._service.delete(superuser)

<<<<<<< HEAD
    def reset_password(self, username: str, new_password: str, hasher_fn: PWDHasherFn) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.reset_password(superuser, new_password, hasher_fn)
=======
    def reset_password(self, username: str, new_password: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.reset_password(superuser, new_password)
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
