from sqlalchemy.orm import Query, Session

from app.db import Permission, TenantDB, UserDB
from app.db.permission import PermissionDB
from app.utils.hash import PWDHasherFn

from .generic_user import GenericUserService, UserNotFoundError


class UserService:
    def __init__(
        self, session: Session, generic_service: GenericUserService, tenant: TenantDB
    ) -> None:
        self._db = session
        self._generic_service = generic_service
        self._tenant = tenant

    def get_all(self) -> list[UserDB]:
        return (
            self._db.query(UserDB)
            .filter(UserDB.tenant == self._tenant, UserDB.is_tenant_user)
            .all()
        )

    def _get_usernames_query(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.tenant == self._tenant, UserDB.username.in_(usernames), UserDB.is_tenant_user
        )

        if not query.all():
            message = f"User(s) with username(s) '{', '.join(usernames)}' not found."
            raise UserNotFoundError(message)

        return query

    def get_by_username(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(
                UserDB.tenant == self._tenant, UserDB.username == username, UserDB.is_tenant_user
            )
            .first()
        )

        if not user:
            message = f"User with username '{username}' not found."
            raise UserNotFoundError(message)

        return user

    def update_permissions(self, username: str, permissions: set[Permission]) -> UserDB:
        user_db = self.get_by_username(username)

        permissions_db = (
            self._db.query(PermissionDB).filter(PermissionDB.name.in_(permissions)).all()
        )

        user_db.permissions.clear()
        user_db.permissions = set(permissions_db)

        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def bulk_activate(self, usernames: list[str]) -> list[UserDB]:
        query = self._get_usernames_query(usernames)
        query.update({"is_active": True})
        self._db.commit()

        return query.all()

    def bulk_deactivate(self, usernames: list[str]) -> list[UserDB]:
        query = self._get_usernames_query(usernames)
        query.update({"is_active": False})
        self._db.commit()

        return query.all()

    def bulk_delete(self, usernames: list[str]) -> None:
        query = self._get_usernames_query(usernames)
        self._db.delete(query)
        self._db.commit()

    def create(  # noqa: PLR0913
        self,
        username: str,
        firstname: str,
        lastname: str,
        plain_password: str,
        permissions: set[Permission],
        hasher_fn: PWDHasherFn,
    ) -> UserDB:
        return self._generic_service.create(
            username,
            firstname,
            lastname,
            plain_password=plain_password,
            role="tenant-user",
            permissions=permissions,
            tenant=self._tenant,
            hasher_fn=hasher_fn,
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

    def reset_password(self, username: str, new_password: str, hasher_fn: PWDHasherFn) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.reset_password(user_db, new_password, hasher_fn)
