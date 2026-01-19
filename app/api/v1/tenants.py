from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.pagination import Pagination, get_pagination
from app.api.response import ArrayResponse, ObjectResponse
from app.models.tenant import TenantCreate, TenantFilter, TenantRead, TenantUpdate
from app.services.tenant import OrderBy, TenantService


def get_tenant_service(db: SessionDI) -> TenantService:
    return TenantService(db)


def get_filter_schema(  # noqa: PLR0913
    search__contains: Annotated[str | None, Query()] = None,
    search__notcontains: Annotated[str | None, Query()] = None,
    code__eq: Annotated[str | None, Query()] = None,
    code__ne: Annotated[str | None, Query()] = None,
    phone__contains: Annotated[str | None, Query()] = None,
    phone__notcontains: Annotated[str | None, Query()] = None,
    phone__eq: Annotated[str | None, Query()] = None,
    valid_until__eq: Annotated[datetime | None, Query()] = None,
    valid_until__ne: Annotated[datetime | None, Query()] = None,
    valid_until__gt: Annotated[datetime | None, Query()] = None,
    valid_until__gte: Annotated[datetime | None, Query()] = None,
    valid_until__lt: Annotated[datetime | None, Query()] = None,
    valid_until__lte: Annotated[datetime | None, Query()] = None,
) -> TenantFilter:
    return TenantFilter(
        search__contains=search__contains,
        search__notcontains=search__notcontains,
        code__eq=code__eq,
        code__ne=code__ne,
        phone__contains=phone__contains,
        phone__notcontains=phone__notcontains,
        phone__eq=phone__eq,
        valid_until__eq=valid_until__eq,
        valid_until__ne=valid_until__ne,
        valid_until__gt=valid_until__gt,
        valid_until__gte=valid_until__gte,
        valid_until__lt=valid_until__lt,
        valid_until__lte=valid_until__lte,
    )


router = APIRouter()


@router.get("/", response_model=ArrayResponse[list[TenantRead]])
def get_all(  # noqa: PLR0913
    request: Request,
    service: Annotated[TenantService, Depends(get_tenant_service)],
    pagination: Annotated[Pagination, Depends(get_pagination)],
    filter_schema: Annotated[TenantFilter, Depends(get_filter_schema)],
    filtering_kind: Annotated[Literal["and", "or"], Query()] = "and",
    order_by: list[OrderBy] = Query(default=[OrderBy.NAME_ASC]),  # noqa: B008, FAST002
):
    items, total_items_count = service.get_all(order_by, filter_schema, filtering_kind, pagination)
    return ArrayResponse(
        items=items,
        total_items_count=total_items_count,
        request=request,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/",
    response_model=ObjectResponse[TenantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(
    service: Annotated[TenantService, Depends(get_tenant_service)], create_schema: TenantCreate
):
    return ObjectResponse(item=service.create(create_schema))


@router.get("/{code}", response_model=ObjectResponse[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_code(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return ObjectResponse(item=service.get_by_code(code))


@router.put(
    "/{code}",
    response_model=ObjectResponse[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(
    service: Annotated[TenantService, Depends(get_tenant_service)],
    code: str,
    update_schema: TenantUpdate,
):
    return ObjectResponse(item=service.update(code, update_schema))


@router.patch(
    "/{code}/activate",
    response_model=ObjectResponse[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return ObjectResponse(item=service.activate(code))


@router.patch(
    "/{code}/deactivate",
    response_model=ObjectResponse[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return ObjectResponse(item=service.deactivate(code))


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    service.delete(code)
