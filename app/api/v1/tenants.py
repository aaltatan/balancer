from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_superuser
from app.db import get_db
from app.models import Response
from app.models.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services.tenant import TenantAlreadyExistsError, TenantNotFoundError, TenantService


def get_tenant_service(db: Annotated[Session, Depends(get_db)]) -> TenantService:
    return TenantService(db)


Service = Annotated[TenantService, Depends(get_tenant_service)]

router = APIRouter()


@router.get(
    "/",
    response_model=Response[list[TenantRead]],
    dependencies=[Depends(get_superuser)],
)
def get_all(service: Service):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[TenantRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_superuser)],
)
def create(service: Service, tenant: TenantCreate):
    try:
        return Response(data=service.create(tenant.name, tenant.valid_from, tenant.valid_to))
    except TenantAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get(
    "/{slug}",
    response_model=Response[TenantRead],
    dependencies=[Depends(get_superuser)],
)
def get_by_slug(service: Service, slug: str):
    try:
        return Response(data=service.get_by_slug(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{slug}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_superuser)],
)
def update(service: Service, slug: str, tenant: TenantUpdate):
    try:
        return Response(data=service.update(slug, tenant.name, tenant.valid_from, tenant.valid_to))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_superuser)],
)
def activate(service: Service, slug: str):
    try:
        return Response(data=service.activate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_superuser)],
)
def deactivate(service: Service, slug: str):
    try:
        return Response(data=service.deactivate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_superuser)],
)
def delete(service: Service, slug: str):
    try:
        service.delete(slug)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
