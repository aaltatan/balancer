from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.responses import get_export_response
from app.db.tenant import TenantDB
from app.filters import FieldsMapper
from app.models import Response
from app.models.tenant import TenantCreate, TenantExport, TenantFilter, TenantRead, TenantUpdate
from app.services.tenant import TenantService
from app.utils.export import ExportType


def get_tenant_service(db: SessionDI) -> TenantService:
    return TenantService(db)


def get_fields_mapper() -> FieldsMapper:
    return {
        "search": TenantDB.search,
        "code": TenantDB.code,
        "phone": TenantDB.phone,
        "valid_until": TenantDB.valid_until,
    }


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


@router.get("/", response_model=Response[list[TenantRead]])
def get_all(
    service: Annotated[TenantService, Depends(get_tenant_service)],
    fields_mapper: Annotated[FieldsMapper, Depends(get_fields_mapper)],
    filter_schema: Annotated[TenantFilter, Depends(get_filter_schema)],
    filtering_kind: Annotated[Literal["and", "or"], Query(alias="filtering-kind")] = "and",
    export: Annotated[ExportType | None, Query()] = None,
):
    data = service.get_all(filter_schema, fields_mapper, filtering_kind)

    if export:
        return get_export_response(export, data, TenantExport, "tenants")

    return Response(data=data)


@router.post(
    "/",
    response_model=Response[TenantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(
    service: Annotated[TenantService, Depends(get_tenant_service)], create_schema: TenantCreate
):
    return Response(data=service.create(create_schema))


@router.get("/{code}", response_model=Response[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_code(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return Response(data=service.get_by_code(code))


@router.put(
    "/{code}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(
    service: Annotated[TenantService, Depends(get_tenant_service)],
    code: str,
    update_schema: TenantUpdate,
):
    return Response(data=service.update(code, update_schema))


@router.patch(
    "/{code}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return Response(data=service.activate(code))


@router.patch(
    "/{code}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    return Response(data=service.deactivate(code))


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: Annotated[TenantService, Depends(get_tenant_service)], code: str):
    service.delete(code)
