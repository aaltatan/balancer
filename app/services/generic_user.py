from sqlalchemy.orm import Session

from app.db import Permission, PermissionDB, Role, TenantDB, UserDB
<<<<<<< HEAD
from app.utils.hash import PWDHasherFn
=======
from app.utils.hash import hash_password
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225


class MoreThanOneSuperuserError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class GenericUserService:
    def __init__(self, session: Session) -> None:
        self._db = session

    def create(  # noqa: PLR0913
        self,
        username: str,
        firstname: str,
        lastname: str,
        plain_password: str,
        *,
        role: Role,
<<<<<<< HEAD
        hasher_fn: PWDHasherFn,
=======
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
        tenant: TenantDB | None = None,
        permissions: set[Permission] | None = None,
    ) -> UserDB:
        user_db_exists_query = self._db.query(UserDB).filter(UserDB.username == username)

        if tenant:
            user_db_exists_query = user_db_exists_query.filter(UserDB.tenant == tenant)

        user_db_exists = user_db_exists_query.first()

        if user_db_exists:
            message = "Unable to create account. Please try different credentials."
            raise UserAlreadyExistsError(message)

        user_db = UserDB(
            username=username,
            firstname=firstname,
            lastname=lastname,
            role=role,
<<<<<<< HEAD
            hashed_password=hasher_fn(plain_password),
=======
            hashed_password=hash_password(plain_password),
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
        )

        if permissions:
            user_db.permissions = set(
                self._db.query(PermissionDB).filter(PermissionDB.name.in_(permissions)).all()
            )

        if tenant:
            user_db.tenant = tenant

        self._db.add(user_db)
        self._db.commit()

        return user_db

    def update(
        self, user_db: UserDB, firstname: str | None = None, lastname: str | None = None
    ) -> UserDB:
        if not firstname and not lastname:
            return user_db

        if firstname:
            user_db.firstname = firstname

        if lastname:
            user_db.lastname = lastname

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

<<<<<<< HEAD
    def reset_password(self, user_db: UserDB, new_password: str, hasher_fn: PWDHasherFn) -> UserDB:
        user_db.hashed_password = hasher_fn(new_password)
=======
    def reset_password(self, user_db: UserDB, new_password: str) -> UserDB:
        user_db.hashed_password = hash_password(new_password)
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225

        self._db.commit()

        return user_db
