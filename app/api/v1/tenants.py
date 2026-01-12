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


@router.get("/{slug}", response_model=Response[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_slug(service: _TenantService, slug: str):
    try:
        return Response(data=service.get_by_slug(slug))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{slug}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(service: _TenantService, slug: str, update_schema: TenantUpdate):
    try:
        return Response(data=service.update(slug, update_schema))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: _TenantService, slug: str):
    try:
        return Response(data=service.activate(slug))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: _TenantService, slug: str):
    try:
        return Response(data=service.deactivate(slug))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: _TenantService, slug: str):
    try:
        service.delete(slug)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
