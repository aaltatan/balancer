from sqlalchemy.orm import Query, Session

from app.db import UserDB
from app.db.tenant import TenantDB
from app.exceptions import BulkNotFoundError, NotFoundError, UserAlreadyExistsError
from app.filters import get_criterion, get_order_by

from ._interfaces import FilteringType, IPaginationSchema, ISchema, IUserCreateSchema
from .generic_user import GenericUserService
from .user import FILTERS_FIELDS_MAPPER, ORDER_BY_FIELDS_MAPPER, OrderBy


class TenantSuperuserService:
    def __init__(
        self, session: Session, user_service: GenericUserService, tenant: TenantDB
    ) -> None:
        self._db = session
        self._service = user_service
        self._tenant = tenant

    def get_all(
        self,
        order_by: list[OrderBy] | None = None,
        filter_schema: ISchema | None = None,
        filtering_kind: FilteringType = "and",
        pagination_schema: IPaginationSchema | None = None,
    ) -> tuple[list[UserDB], int]:
        query = self._db.query(UserDB)

        if order_by:
            query = query.order_by(*get_order_by(order_by, ORDER_BY_FIELDS_MAPPER))

        if filter_schema:
            query = query.filter(
                get_criterion(FILTERS_FIELDS_MAPPER, filter_schema, kind=filtering_kind)
            )

        count = query.count()

        if pagination_schema:
            query = query.offset(pagination_schema.offset).limit(pagination_schema.limit)

        return query.all(), count

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
            raise NotFoundError(object_name="user", fieldname="username", field_value=username)

        return user

    def _get_usernames_query(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.username.in_(usernames), UserDB.is_tenant_superuser
        )

        if not query.all():
            raise BulkNotFoundError(object_name="user", fieldname="username", field_value=usernames)

        return query

    def create(self, *, schema: IUserCreateSchema, plain_password: str) -> UserDB:
        user_db_exists = (
            self._db.query(UserDB)
            .filter(UserDB.username == schema.username, UserDB.tenant == self._tenant)
            .first()
        )

        if user_db_exists:
            raise UserAlreadyExistsError

        return self._service.create(
            schema=schema,
            plain_password=plain_password,
            role="tenant-superuser",
            tenant=self._tenant,
        )

    def update(self, username: str, schema: ISchema) -> UserDB:
        user_db = self.get_by_username(username)
        return self._service.update(user_db, schema)

    def activate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._service.activate(user_db)

    def deactivate(self, username: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._service.deactivate(user_db)

    def delete(self, username: str) -> None:
        user_db = self.get_by_username(username)
        return self._service.delete(user_db)

    def reset_password(self, username: str, plain_password: str) -> UserDB:
        user_db = self.get_by_username(username)
        return self._service.reset_password(user_db, plain_password)
