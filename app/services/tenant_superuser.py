from sqlalchemy.orm import Query, Session

from app.db import UserDB
from app.db.tenant import TenantDB

from .generic_user import GenericUserService, UserAlreadyExistsError, UserNotFoundError
from .tenant import TenantNotFoundError


class TenantSuperuserService:
    def __init__(self, session: Session, generic_service: GenericUserService) -> None:
        self._db = session
        self._generic_service = generic_service

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).filter(UserDB.is_tenant_superuser).all()

    def get_by_username(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(UserDB.username == username, UserDB.is_tenant_superuser)
            .first()
        )

        if not user:
            message = f"User with username '{username}' not found."
            raise UserNotFoundError(message)

        return user

    def _get_usernames_query(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.username.in_(usernames), UserDB.is_tenant_superuser
        )

        if not query.all():
            message = f"User(s) with username(s) '{', '.join(usernames)}' not found."
            raise UserNotFoundError(message)

        return query

    def create(
        self, username: str, firstname: str, lastname: str, plain_password: str, tenant_slug: str
    ) -> UserDB:
        tenant = self._db.query(TenantDB).filter(TenantDB.slug == tenant_slug).first()

        if not tenant:
            message = f"Tenant with slug '{tenant_slug}' not found."
            raise TenantNotFoundError(message)

        user_db_exists = (
            self._db.query(UserDB)
            .filter(UserDB.username == username, UserDB.tenant == tenant)
            .first()
        )

        if user_db_exists:
            message = "Unable to create account. Please try different credentials."
            raise UserAlreadyExistsError(message)

        return self._generic_service.create(
            username, firstname, lastname, plain_password, role="tenant-superuser", tenant=tenant
        )

    def update(
        self, username: str, firstname: str | None = None, lastname: str | None = None
    ) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.update(user_db, firstname, lastname)

    def activate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.activate(user_db)

    def deactivate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.deactivate(user_db)

    def delete(self, username: str) -> None:
        user_db = self.get_by_username(username)
        return self._generic_service.delete(user_db)

    def reset_password(self, username: str, new_password: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.reset_password(user_db, new_password)
