from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.db import PermissionDB, Role, TenantDB, UserDB
from app.exceptions import AlreadyExistsError


class UserCreate(Protocol):
    username: str
    permissions: set[Any]

    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...


class UserUpdate(Protocol):
    def model_dump(*args: Any, **kwargs: Any) -> dict[str, Any]: ...


class GenericUserService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def create(
        self,
        *,
        schema: UserCreate,
        hashed_password: str,
        role: Role,
        tenant: TenantDB | None = None,
    ) -> UserDB:
        user_db_exists_query = self._db.query(UserDB).filter(UserDB.username == schema.username)

        if tenant:
            user_db_exists_query = user_db_exists_query.filter(UserDB.tenant == tenant)

        user_db_exists = user_db_exists_query.first()

        if user_db_exists:
            message = "Unable to create account. Please try different credentials."
            raise AlreadyExistsError(message)

        schema_dict = schema.model_dump()

        permissions = schema_dict.pop("permissions")

        user_db = UserDB(**schema_dict, role=role, hashed_password=hashed_password)

        if permissions:
            user_db.permissions = set(
                self._db.query(PermissionDB).filter(PermissionDB.name.in_(permissions)).all()
            )

        if tenant:
            user_db.tenant = tenant

        self._db.add(user_db)
        self._db.commit()

        return user_db

    def update(self, user_db: UserDB, schema: UserUpdate) -> UserDB:
        for key, value in schema.model_dump().items():
            if value is not None:
                setattr(user_db, key, value)

        self._db.commit()
        self._db.refresh(user_db)

        return user_db

    def activate(self, user_db: UserDB) -> UserDB:
        if user_db.is_active:
            return user_db

        user_db.is_active = True
        self._db.commit()

        return user_db

    def deactivate(self, user_db: UserDB) -> UserDB:
        if not user_db.is_active:
            return user_db

        user_db.is_active = False
        self._db.commit()

        return user_db

    def delete(self, user_db: UserDB) -> None:
        self._db.delete(user_db)
        self._db.commit()

    def reset_password(self, user_db: UserDB, hashed_password: str) -> UserDB:
        user_db.hashed_password = hashed_password

        self._db.commit()

        return user_db
