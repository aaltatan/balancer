from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

<<<<<<< HEAD
from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
=======
from app.api.dependencies.auth import get_superuser
from app.db import get_db
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
from app.models import Response
from app.models.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services.tenant import TenantAlreadyExistsError, TenantNotFoundError, TenantService


def get_tenant_service(db: SessionDI) -> TenantService:
    return TenantService(db)


_TenantService = Annotated[TenantService, Depends(get_tenant_service)]

router = APIRouter()


<<<<<<< HEAD
@router.get("/", response_model=Response[list[TenantRead]], dependencies=[RequireSuperuserDI])
def get_all(service: _TenantService):
=======
@router.get(
    "/",
    response_model=Response[list[TenantRead]],
    dependencies=[Depends(get_superuser)],
)
def get_all(service: Service):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[TenantRead],
    status_code=status.HTTP_201_CREATED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
)
def create(service: _TenantService, tenant: TenantCreate):
=======
    dependencies=[Depends(get_superuser)],
)
def create(service: Service, tenant: TenantCreate):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        return Response(data=service.create(tenant.name, tenant.valid_from, tenant.valid_to))
    except TenantAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


<<<<<<< HEAD
@router.get("/{slug}", response_model=Response[TenantRead], dependencies=[RequireSuperuserDI])
def get_by_slug(service: _TenantService, slug: str):
=======
@router.get(
    "/{slug}",
    response_model=Response[TenantRead],
    dependencies=[Depends(get_superuser)],
)
def get_by_slug(service: Service, slug: str):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        return Response(data=service.get_by_slug(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{slug}",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
)
def update(service: _TenantService, slug: str, tenant: TenantUpdate):
=======
    dependencies=[Depends(get_superuser)],
)
def update(service: Service, slug: str, tenant: TenantUpdate):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        return Response(data=service.update(slug, tenant.name, tenant.valid_from, tenant.valid_to))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/activate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
)
def activate(service: _TenantService, slug: str):
=======
    dependencies=[Depends(get_superuser)],
)
def activate(service: Service, slug: str):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        return Response(data=service.activate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{slug}/deactivate",
    response_model=Response[TenantRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: _TenantService, slug: str):
=======
    dependencies=[Depends(get_superuser)],
)
def deactivate(service: Service, slug: str):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        return Response(data=service.deactivate(slug))
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


<<<<<<< HEAD
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI])
def delete(service: _TenantService, slug: str):
=======
@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_superuser)],
)
def delete(service: Service, slug: str):
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    try:
        service.delete(slug)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
