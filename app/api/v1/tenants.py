from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.exceptions import AlreadyExistsError, NotFoundError
from app.models import Response
from app.models.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services.tenant import TenantService


def get_tenant_service(db: SessionDI) -> TenantService:
    return TenantService(db)


_TenantService = Annotated[TenantService, Depends(get_tenant_service)]

router = APIRouter()


@router.get("/", response_model=Response[list[TenantRead]], dependencies=[RequireSuperuserDI])
def get_all(service: _TenantService):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[TenantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(service: _TenantService, create_schema: TenantCreate):
    try:
        return Response(data=service.create(create_schema))
    except AlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from None


@router.get("/{code}", response_model=Response[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_code(service: _TenantService, code: str):
    try:
        return Response(data=service.get_by_code(code))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{code}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(service: _TenantService, code: str, update_schema: TenantUpdate):
    try:
        return Response(data=service.update(code, update_schema))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{code}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: _TenantService, code: str):
    try:
        return Response(data=service.activate(code))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{code}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: _TenantService, code: str):
    try:
        return Response(data=service.deactivate(code))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: _TenantService, code: str):
    try:
        service.delete(code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
