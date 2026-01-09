from sqlalchemy.orm import Query, Session

from app.db import Permission, PermissionDB, Role, TenantDB, UserDB
from app.utils.hash import hash_password


class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, session: Session, tenant: TenantDB) -> None:
        self._db = session
        self._tenant = tenant

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).filter(UserDB.tenant == self._tenant).all()

    def get_by_username(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(UserDB.tenant == self._tenant, UserDB.username == username)
            .first()
        )

        if not user:
            message = f"User with username '{username}' not found."
            raise UserNotFoundError(message)

        return user

    def _create(  # noqa: PLR0913
        self,
        username: str,
        firstname: str,
        lastname: str,
        password: str,
        permissions: set[Permission] | None = None,
        role: Role = "tenant-user",
    ) -> UserDB:
        if not permissions:
            permissions = set()

        user_db_exists = (
            self._db.query(UserDB)
            .filter(UserDB.username == username, UserDB.tenant == self._tenant)
            .first()
        )

        if user_db_exists:
            message = f"User with username '{username}' already exists."
            raise UserAlreadyExistsError(message)

        user_db = UserDB(
            username=username,
            firstname=firstname,
            lastname=lastname,
            role=role,
            hashed_password=hash_password(password),
            permissions=set(
                self._db.query(PermissionDB).filter(PermissionDB.name.in_(permissions)).all()
            ),
            tenant=self._tenant,
        )

        self._db.add(user_db)
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def create_tenant_superuser(
        self, username: str, firstname: str, lastname: str, password: str
    ) -> UserDB:
        return self._create(username, firstname, lastname, password, role="tenant-superuser")

    def create_tenant_user(
        self,
        username: str,
        firstname: str,
        lastname: str,
        password: str,
        permissions: set[Permission],
    ) -> UserDB:
        return self._create(username, firstname, lastname, password, permissions)

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

    def update(
        self, username: str, firstname: str | None = None, lastname: str | None = None
    ) -> UserDB:
        user_db = self.get_by_username(username)

        if not firstname and not lastname:
            return user_db

        if firstname:
            user_db.firstname = firstname

        if lastname:
            user_db.lastname = lastname

        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def activate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)

        if user_db.is_active:
            return user_db

        user_db.is_active = True
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def deactivate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)

        if not user_db.is_active:
            return user_db

        user_db.is_active = False
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def reset_password(self, username: str, new_password: str) -> UserDB:
        user_db = self.get_by_username(username)
        user_db.hashed_password = hash_password(new_password)
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def delete(self, username: str) -> None:
        user_db = self.get_by_username(username)
        self._db.delete(user_db)
        self._db.commit()

    def _get_usernames(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.tenant == self._tenant, UserDB.username.in_(usernames)
        )

        if not query.all():
            message = f"User(s) with username(s) '{', '.join(usernames)}' not found."
            raise UserNotFoundError(message)

        return query

    def bulk_activate(self, usernames: list[str]) -> list[UserDB]:
        query = self._get_usernames(usernames)
        query.update({"is_active": True})
        self._db.commit()
        self._db.refresh(query)

        return query.all()

    def bulk_deactivate(self, usernames: list[str]) -> list[UserDB]:
        query = self._get_usernames(usernames)
        query.update({"is_active": False})
        self._db.commit()
        self._db.refresh(query)

        return query.all()

    def bulk_delete(self, usernames: list[str]) -> None:
        query = self._get_usernames(usernames)
        self._db.delete(query)
        self._db.commit()

    def empty(self) -> None:
        self._db.query(UserDB).delete()
        self._db.commit()
