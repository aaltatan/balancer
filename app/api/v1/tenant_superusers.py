from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Query, status

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.pagination import Pagination, get_pagination
from app.api.dependencies.tenant import TenantDBFromPathDI
from app.api.dependencies.users import UsernameFromPathDI, get_user_filter_schema
from app.api.dependencies.utils import PWDHasherFnDI, SessionDI
from app.api.response import ObjectResponse, PageResponse
from app.schemas.user import (
    ResetPasswordSchema,
    UserCreateSchema,
    UserFilterSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from app.services.generic_user import GenericUserService
from app.services.tenant_superuser import OrderBy, TenantSuperuserService

router = APIRouter()


def get_tenant_superuser_service(db: SessionDI, hasher_fn: PWDHasherFnDI) -> TenantSuperuserService:
    return TenantSuperuserService(db, GenericUserService(db, hasher_fn))


@router.get("/", response_model=PageResponse[UserReadSchema], dependencies=[RequireSuperuserDI])
def get_all(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    filter_schema: Annotated[UserFilterSchema, Depends(get_user_filter_schema)],
    pagination: Annotated[Pagination, Depends(get_pagination)],
    filtering_kind: Annotated[Literal["and", "or"], Query()] = "and",
    order_by: list[OrderBy] = Query(default=[OrderBy.USERNAME_ASC]),  # noqa: B008, FAST002
):
    items, total_items_count = service.get_all(order_by, filter_schema, filtering_kind, pagination)
    return PageResponse(
        items=items,
        total_items_count=total_items_count,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/{code}",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    create_schema: Annotated[UserCreateSchema, Body(embed=False)],
    tenant: TenantDBFromPathDI,
):
    user = service.create(
        schema=create_schema,
        plain_password=create_schema.password.get_secret_value(),
        tenant=tenant,
    )
    return ObjectResponse(item=user)


@router.get(
    "/{code}/{username}",
    response_model=ObjectResponse[UserReadSchema],
    dependencies=[RequireSuperuserDI],
)
def get_by_username(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    tenant: TenantDBFromPathDI,
):
    user = service.get_by_username(username, tenant)
    return ObjectResponse(item=user)


@router.put(
    "/{code}/{username}",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    update_schema: UserUpdateSchema,
    tenant: TenantDBFromPathDI,
):
    user = service.update(username, update_schema, tenant)
    return ObjectResponse(item=user)


@router.patch(
    "/{code}/{username}/activate",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    tenant: TenantDBFromPathDI,
):
    user = service.activate(username, tenant)
    return ObjectResponse(item=user)


@router.patch(
    "/{code}/{username}/deactivate",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    tenant: TenantDBFromPathDI,
):
    user = service.deactivate(username, tenant)
    return ObjectResponse(item=user)


@router.patch(
    "/{code}/{username}/reset-password",
    response_model=ObjectResponse[UserReadSchema],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def reset_password(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    schema: ResetPasswordSchema,
    tenant: TenantDBFromPathDI,
):
    user = service.reset_password(username, schema.new_password.get_secret_value(), tenant)
    return ObjectResponse(item=user)


@router.delete(
    "/{code}/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[RequireSuperuserDI],
)
def delete(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: UsernameFromPathDI,
    tenant: TenantDBFromPathDI,
):
    service.delete(username, tenant)
