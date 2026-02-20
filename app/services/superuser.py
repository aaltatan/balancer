from sqlalchemy.orm import Session

from app.db import UserDB
from app.exceptions import NotFoundError

from ._interfaces import ISchema, IUserCreateSchema
from .generic_user import GenericUserService


class SuperuserService:
    def __init__(self, session: Session, service: GenericUserService) -> None:
        self._db = session
        self._service = service

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).filter(UserDB.role == "superuser").all()

    def create(self, *, schema: IUserCreateSchema, plain_password: str) -> UserDB:
        return self._service.create(schema=schema, plain_password=plain_password, role="superuser")

    def update(self, username: str, schema: ISchema) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.update(superuser, schema)

    def activate(self, username: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.activate(superuser)

    def deactivate(self, username: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.deactivate(superuser)

    def delete(self, username: str) -> None:
        superuser = self._get_superuser(username)
        return self._service.delete(superuser)

    def reset_password(self, username: str, plain_password: str) -> UserDB:
        superuser = self._get_superuser(username)
        return self._service.reset_password(superuser, plain_password)

    def _get_superuser(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(UserDB.role == "superuser", UserDB.username == username)
            .first()
        )

        if not user:
            raise NotFoundError(object_name="user", fieldname="username", field_value=username)

        return user
