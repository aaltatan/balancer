from sqlalchemy.orm import Query, Session

from balancer.domain.exceptions import AlreadyExistsError, NotFoundError
from balancer.domain.models import UserDB
from balancer.domain.models.tenant import TenantDB

from .generic_user import GenericUserService, UserCreate, UserUpdate


class TenantSuperuserService:
    def __init__(
        self, session: Session, generic_service: GenericUserService, tenant: TenantDB
    ) -> None:
        self._db = session
        self._generic_service = generic_service
        self._tenant = tenant

    def get_all(self) -> list[UserDB]:
        return self._db.query(UserDB).filter(UserDB.is_tenant_superuser).all()

    def get_by_username(self, username: str) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(
                UserDB.username == username,
                UserDB.is_tenant_superuser,
                UserDB.tenant == self._tenant,
            )
            .first()
        )

        if not user:
            message = f"User with username '{username}' not found."
            raise NotFoundError(message)

        return user

    def _get_usernames_query(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.username.in_(usernames), UserDB.is_tenant_superuser
        )

        if not query.all():
            message = f"User(s) with username(s) '{', '.join(usernames)}' not found."
            raise NotFoundError(message)

        return query

    def create(self, *, schema: UserCreate, plain_password: str) -> UserDB:
        user_db_exists = (
            self._db.query(UserDB)
            .filter(UserDB.username == schema.username, UserDB.tenant == self._tenant)
            .first()
        )

        if user_db_exists:
            message = "Unable to create account. Please try different credentials."
            raise AlreadyExistsError(message)

        return self._generic_service.create(
            schema=schema,
            plain_password=plain_password,
            role="tenant-superuser",
            tenant=self._tenant,
        )

    def update(self, username: str, schema: UserUpdate) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.update(user_db, schema)

    def activate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.activate(user_db)

    def deactivate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.deactivate(user_db)

    def delete(self, username: str) -> None:
        user_db = self.get_by_username(username)
        return self._generic_service.delete(user_db)

    def reset_password(self, username: str, plain_password: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._generic_service.reset_password(user_db, plain_password)
