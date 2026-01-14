from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.responses import get_export_response
from app.models import Response
from app.models.tenant import TenantCreate, TenantExport, TenantRead, TenantUpdate
from app.services.tenant import TenantService
from app.utils.export import ExportType


def get_tenant_service(db: SessionDI) -> TenantService:
    return TenantService(db)


_TenantService = Annotated[TenantService, Depends(get_tenant_service)]

router = APIRouter()


class QueryParams(BaseModel):
    export: ExportType | None = None


@router.get("/", response_model=Response[list[TenantRead]])
def get_all(service: _TenantService, params: Annotated[QueryParams, Query()]):
    data = service.get_all()

    if params.export:
        return get_export_response(params.export, data, TenantExport, "tenants")

    return Response(data=data)


@router.post(
    "/",
    response_model=Response[TenantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(service: _TenantService, create_schema: TenantCreate):
    return Response(data=service.create(create_schema))


@router.get("/{code}", response_model=Response[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_code(service: _TenantService, code: str):
    return Response(data=service.get_by_code(code))


@router.put(
    "/{code}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(service: _TenantService, code: str, update_schema: TenantUpdate):
    return Response(data=service.update(code, update_schema))


@router.patch(
    "/{code}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: _TenantService, code: str):
    return Response(data=service.activate(code))


@router.patch(
    "/{code}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: _TenantService, code: str):
    return Response(data=service.deactivate(code))


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: _TenantService, code: str):
    service.delete(code)
