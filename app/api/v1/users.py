from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Form, Query, status

from app.api.dependencies.auth import RequireAnySuperuserDI
from app.api.dependencies.pagination import Pagination, get_pagination
from app.api.dependencies.tenant import TenantDBFromTokenDI
from app.api.dependencies.users import UsernameFromPathDI, get_user_filter_schema
from app.api.dependencies.utils import PWDHasherFnDI, SessionDI
from app.api.response import ArrayResponse, ObjectResponse, PageResponse
from app.schemas.user import (
    ResetPasswordSchema,
    UserCreateSchema,
    UserFilterSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from app.services.generic_user import GenericUserService
from app.services.user import OrderBy, UserService

router = APIRouter()


def get_user_service(
    db: SessionDI, tenant: TenantDBFromTokenDI, hasher_fn: PWDHasherFnDI
) -> UserService:
    return UserService(db, GenericUserService(db, hasher_fn), tenant)


@router.get("/", response_model=PageResponse[UserReadSchema], dependencies=[RequireAnySuperuserDI])
def get_all(
    service: Annotated[UserService, Depends(get_user_service)],
    filter_schema: Annotated[UserFilterSchema, Depends(get_user_filter_schema)],
    pagination: Annotated[Pagination, Depends(get_pagination)],
    filtering_kind: Annotated[Literal["and", "or"], Query()] = "and",
    order_by: list[OrderBy] = Query(default=[OrderBy.USERNAME_ASC]),  # noqa: B008, FAST002
):
    items, total_items_count = service.get_all(
        order_by=order_by,
        filter_schema=filter_schema,
        filtering_kind=filtering_kind,
        pagination_schema=pagination,
    )
    return PageResponse(
        items=items,
        total_items_count=total_items_count,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAnySuperuserDI],
)
def create(
    service: Annotated[UserService, Depends(get_user_service)], create_schema: UserCreateSchema
):
    return ObjectResponse(
        item=service.create(
            schema=create_schema, plain_password=create_schema.password.get_secret_value()
        )
    )


@router.get(
    "/{username}",
    response_model=ObjectResponse[UserReadSchema],
    dependencies=[RequireAnySuperuserDI],
)
def get_by_username(
    service: Annotated[UserService, Depends(get_user_service)], username: UsernameFromPathDI
):
    return ObjectResponse(item=service.get_by_username(username))


@router.put(
    "/{username}",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def update(
    service: Annotated[UserService, Depends(get_user_service)],
    username: UsernameFromPathDI,
    update_schema: UserUpdateSchema,
):
    return ObjectResponse(item=service.update(username, update_schema))


@router.patch(
    "/{username}/activate",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def activate(
    service: Annotated[UserService, Depends(get_user_service)], username: UsernameFromPathDI
):
    return ObjectResponse(item=service.activate(username))


@router.patch(
    "/{username}/deactivate",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def deactivate(
    service: Annotated[UserService, Depends(get_user_service)], username: UsernameFromPathDI
):
    return ObjectResponse(item=service.deactivate(username))


@router.patch(
    "/{username}/reset-password",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def reset_password(
    service: Annotated[UserService, Depends(get_user_service)],
    username: UsernameFromPathDI,
    schema: Annotated[ResetPasswordSchema, Form()],
):
    return ObjectResponse(
        item=service.reset_password(username, schema.new_password.get_secret_value())
    )


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def delete(
    service: Annotated[UserService, Depends(get_user_service)], username: UsernameFromPathDI
):
    service.delete(username)


@router.patch(
    "/bulk/activate",
    response_model=ArrayResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_activate(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    return ArrayResponse(items=service.bulk_activate(usernames))


@router.patch(
    "/bulk/deactivate",
    response_model=ArrayResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_deactivate(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    return ArrayResponse(items=service.bulk_deactivate(usernames))


@router.delete(
    "/bulk/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def bulk_delete(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    service.bulk_delete(usernames)
