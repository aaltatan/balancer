from datetime import datetime
from typing import Annotated

from fastapi import Query

from app.schemas.user import UserFilterSchema


def get_user_filter_schema(  # noqa: PLR0913
    search__contains: Annotated[str | None, Query()] = None,
    search__notcontains: Annotated[str | None, Query()] = None,
    username__eq: Annotated[str | None, Query()] = None,
    username__ne: Annotated[str | None, Query()] = None,
    firstname__eq: Annotated[str | None, Query()] = None,
    firstname__ne: Annotated[str | None, Query()] = None,
    lastname__eq: Annotated[str | None, Query()] = None,
    lastname__ne: Annotated[str | None, Query()] = None,
    is_active__eq: Annotated[bool | None, Query()] = None,
    is_active__ne: Annotated[bool | None, Query()] = None,
    role__eq: Annotated[str | None, Query()] = None,
    role__ne: Annotated[str | None, Query()] = None,
    created_at__eq: Annotated[datetime | None, Query()] = None,
    created_at__ne: Annotated[datetime | None, Query()] = None,
    created_at__gt: Annotated[datetime | None, Query()] = None,
    created_at__gte: Annotated[datetime | None, Query()] = None,
    created_at__lt: Annotated[datetime | None, Query()] = None,
    created_at__lte: Annotated[datetime | None, Query()] = None,
    updated_at__eq: Annotated[datetime | None, Query()] = None,
    updated_at__ne: Annotated[datetime | None, Query()] = None,
    updated_at__gt: Annotated[datetime | None, Query()] = None,
    updated_at__gte: Annotated[datetime | None, Query()] = None,
    updated_at__lt: Annotated[datetime | None, Query()] = None,
    updated_at__lte: Annotated[datetime | None, Query()] = None,
) -> UserFilterSchema:
    return UserFilterSchema(
        search__contains=search__contains,
        search__notcontains=search__notcontains,
        username__eq=username__eq,
        username__ne=username__ne,
        firstname__eq=firstname__eq,
        firstname__ne=firstname__ne,
        lastname__eq=lastname__eq,
        lastname__ne=lastname__ne,
        is_active__eq=is_active__eq,
        is_active__ne=is_active__ne,
        role__eq=role__eq,
        role__ne=role__ne,
        created_at__eq=created_at__eq,
        created_at__ne=created_at__ne,
        created_at__gt=created_at__gt,
        created_at__gte=created_at__gte,
        created_at__lt=created_at__lt,
        created_at__lte=created_at__lte,
        updated_at__eq=updated_at__eq,
        updated_at__ne=updated_at__ne,
        updated_at__gt=updated_at__gt,
        updated_at__gte=updated_at__gte,
        updated_at__lt=updated_at__lt,
        updated_at__lte=updated_at__lte,
    )
