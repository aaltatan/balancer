from enum import StrEnum

from sqlalchemy.orm import Query, Session

from app.db import Permission, TenantDB, UserDB
from app.db.permission import PermissionDB
from app.exceptions import BulkNotFoundError, NotFoundError
from app.filters import get_criterion, get_order_by

from ._interfaces import (
    FilteringType,
    IFilterSchema,
    IPaginationSchema,
    IUpdateSchema,
    IUserCreateSchema,
)
from .generic_user import GenericUserService


class OrderBy(StrEnum):
    USERNAME_ASC = "username"
    USERNAME_DESC = "username (desc)"
    FIRSTNAME_ASC = "firstname"
    FIRSTNAME_DESC = "firstname (desc)"
    LASTNAME_ASC = "lastname"
    LASTNAME_DESC = "lastname (desc)"
    IS_ACTIVE_ASC = "is active"
    IS_ACTIVE_DESC = "is active (desc)"
    ROLE_ASC = "role"
    ROLE_DESC = "role (desc)"
    CREATED_AT_ASC = "created at"
    CREATED_AT_DESC = "created at (desc)"
    UPDATED_AT_ASC = "updated at"
    UPDATED_AT_DESC = "updated at (desc)"


ORDER_BY_FIELDS_MAPPER = {
    OrderBy.USERNAME_ASC: UserDB.username,
    OrderBy.USERNAME_DESC: UserDB.username.desc(),
    OrderBy.FIRSTNAME_ASC: UserDB.firstname,
    OrderBy.FIRSTNAME_DESC: UserDB.firstname.desc(),
    OrderBy.LASTNAME_ASC: UserDB.lastname,
    OrderBy.LASTNAME_DESC: UserDB.lastname.desc(),
    OrderBy.IS_ACTIVE_ASC: UserDB.is_active,
    OrderBy.IS_ACTIVE_DESC: UserDB.is_active.desc(),
    OrderBy.ROLE_ASC: UserDB.role,
    OrderBy.ROLE_DESC: UserDB.role.desc(),
    OrderBy.CREATED_AT_ASC: UserDB.created_at,
    OrderBy.CREATED_AT_DESC: UserDB.created_at.desc(),
    OrderBy.UPDATED_AT_ASC: UserDB.updated_at,
    OrderBy.UPDATED_AT_DESC: UserDB.updated_at.desc(),
}


FILTERS_FIELDS_MAPPER = {
    "username": UserDB.username,
    "firstname": UserDB.firstname,
    "lastname": UserDB.lastname,
    "is_active": UserDB.is_active,
    "role": UserDB.role,
    "created_at": UserDB.created_at,
    "updated_at": UserDB.updated_at,
}


class UserService:
    def __init__(
        self, session: Session, generic_service: GenericUserService, tenant: TenantDB
    ) -> None:
        self._db = session
        self._generic_service = generic_service
        self._tenant = tenant

    def get_all(
        self,
        order_by: list[OrderBy] | None = None,
        filter_schema: IFilterSchema | None = None,
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

    def _get_usernames_query(self, usernames: list[str]) -> Query[UserDB]:
        query = self._db.query(UserDB).filter(
            UserDB.tenant == self._tenant, UserDB.username.in_(usernames), UserDB.is_tenant_user
        )

        if not query.all():
            raise BulkNotFoundError(object_name="user", fieldname="username", field_value=usernames)

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
            raise NotFoundError(object_name="user", fieldname="username", field_value=username)

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

    def create(self, *, schema: IUserCreateSchema, plain_password: str) -> UserDB:
        return self._generic_service.create(
            schema=schema, plain_password=plain_password, role="tenant-user", tenant=self._tenant
        )

    def update(self, username: str, schema: IUpdateSchema) -> UserDB:
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
