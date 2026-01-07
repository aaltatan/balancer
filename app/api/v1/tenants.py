from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Response
from app.models.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services.tenant import TenantAlreadyExistsError, TenantNotFoundError, TenantService


def get_tenant_service(db: Annotated[Session, Depends(get_db)]) -> TenantService:
    return TenantService(db)


Service = Annotated[TenantService, Depends(get_tenant_service)]

router = APIRouter()


@router.get("/", response_model=Response[list[TenantRead]])
def get_tenants(service: Service):
    return Response(data=service.get_all())


@router.post("/", response_model=Response[TenantRead], status_code=status.HTTP_201_CREATED)
def create_tenant(service: Service, tenant: TenantCreate):
    try:
        return Response(data=service.create(tenant))
    except TenantAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{slug}", response_model=Response[TenantRead])
def get_tenant(service: Service, slug: str):
    try:
        return Response(data=service.get_by_slug(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put("/{slug}", response_model=Response[TenantRead], status_code=status.HTTP_202_ACCEPTED)
def update_tenant(service: Service, slug: str, tenant: TenantUpdate):
    try:
        return Response(data=service.update(slug, tenant))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/activate", response_model=Response[TenantRead], status_code=status.HTTP_202_ACCEPTED
)
def activate_tenant(service: Service, slug: str):
    try:
        return Response(data=service.activate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/deactivate", response_model=Response[TenantRead], status_code=status.HTTP_202_ACCEPTED
)
def deactivate_tenant(service: Service, slug: str):
    try:
        return Response(data=service.deactivate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(service: Service, slug: str):
    try:
        service.delete(slug)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
