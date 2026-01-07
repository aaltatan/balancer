from sqlalchemy.orm import Query, Session

from app.db.permission import Permission, PermissionDB
from app.db.user import Role, UserDB
from app.models.user import ResetPassword, UserCreate, UserUpdate
from app.utils.hash import hash_password


class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).all()

    def get_by_username(self, username: str) -> UserDB:
        user = self._db.query(UserDB).filter(UserDB.username == username).first()

        if not user:
            message = f"User with username '{username}' not found."
            raise UserNotFoundError(message)

        return user

    def _create(self, user: UserCreate, role: Role = "tenant-user") -> UserDB:
        user_db_exists = self._db.query(UserDB).filter(UserDB.username == user.username).first()

        if user_db_exists:
            message = f"User with username '{user.username}' already exists."
            raise UserAlreadyExistsError(message)

        model_dict = user.model_dump()

        password = model_dict.pop("password")
        hashed_password = hash_password(password.get_secret_value())

        user_db_kwargs = {**model_dict, "role": role, "hashed_password": hashed_password}

        if role in {"superuser", "tenant-superuser"}:
            user_db_kwargs["permissions"] = set()
        else:
            permissions = model_dict.pop("permissions")
            permissions_db = (
                self._db.query(PermissionDB).filter(PermissionDB.name.in_(permissions)).all()
            )
            user_db_kwargs["permissions"] = set(permissions_db)

        user_db = UserDB(**user_db_kwargs)

        self._db.add(user_db)
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def create_superuser(self, user: UserCreate) -> UserDB:
        return self._create(user, role="superuser")

    def create_tenant_superuser(self, user: UserCreate) -> UserDB:
        return self._create(user, role="tenant-superuser")

    def create_tenant_user(self, user: UserCreate) -> UserDB:
        return self._create(user, role="tenant-user")

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

    def update(self, username: str, user: UserUpdate) -> UserDB:
        user_db = self.get_by_username(username)

        for key, value in user.model_dump().items():
            if value is not None:
                setattr(user_db, key, value)

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

    def reset_password(self, username: str, schema: ResetPassword) -> UserDB:
        user_db = self.get_by_username(username)
        user_db.hashed_password = hash_password(schema.new_password.get_secret_value())
        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def delete(self, username: str) -> None:
        user_db = self.get_by_username(username)
        self._db.delete(user_db)
        self._db.commit()

    def _get_usernames(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(UserDB.username.in_(usernames))

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
