from sqlalchemy.orm import Session

from app.db import UserDB
from app.db.tenant import TenantDB
from app.exceptions import NotFoundError
from app.filters import get_criterion, get_order_by

from ._interfaces import FilteringType, IPaginationSchema, ISchema, IUserCreateSchema
from .generic_user import GenericUserService
from .user import FILTERS_FIELDS_MAPPER, ORDER_BY_FIELDS_MAPPER, OrderBy


class TenantSuperuserService:
    def __init__(self, session: Session, user_service: GenericUserService) -> None:
        self._db = session
        self._service = user_service

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

    def get_by_username(self, username: str, tenant: TenantDB) -> UserDB:
        user = (
            self._db.query(UserDB)
            .filter(
                UserDB.username == username,
                UserDB.tenant == tenant,
                UserDB.is_tenant_superuser,
            )
            .first()
        )

        if not user:
            raise NotFoundError(object_name="user", fieldname="username", field_value=username)

        return user

    def create(self, *, schema: IUserCreateSchema, plain_password: str, tenant: TenantDB) -> UserDB:
        return self._service.create(
            schema=schema,
            plain_password=plain_password,
            role="tenant-superuser",
            tenant=tenant,
        )

    def update(self, username: str, schema: ISchema, tenant: TenantDB) -> UserDB:
        user_db = self.get_by_username(username, tenant)
        return self._service.update(user_db, schema)

    def activate(self, username: str, tenant: TenantDB) -> UserDB:
        user_db = self.get_by_username(username, tenant)
        return self._service.activate(user_db)

    def deactivate(self, username: str, tenant: TenantDB) -> UserDB:
        user_db = self.get_by_username(username, tenant)
        return self._service.deactivate(user_db)

    def delete(self, username: str, tenant: TenantDB) -> None:
        user_db = self.get_by_username(username, tenant)
        return self._service.delete(user_db)

    def reset_password(self, username: str, plain_password: str, tenant: TenantDB) -> UserDB:
        user_db = self.get_by_username(username, tenant)
        return self._service.reset_password(user_db, plain_password)
