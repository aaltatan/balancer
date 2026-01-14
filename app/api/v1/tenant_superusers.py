from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI
from app.api.dependencies.tenant import ActiveTenantDI
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.generic_user import GenericUserService
from app.services.tenant_superuser import TenantSuperuserService

router = APIRouter()


def get_tenant_superuser_service(
    db: SessionDI, tenant: ActiveTenantDI, hasher_fn: PWDHasherFnDI
) -> TenantSuperuserService:
    return TenantSuperuserService(db, GenericUserService(db, hasher_fn), tenant)


_TenantSuperuserService = Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)]


@router.get("/", response_model=Response[list[UserRead]], dependencies=[RequireSuperuserDI])
def get_all(service: _TenantSuperuserService):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(service: _TenantSuperuserService, create_schema: Annotated[UserCreate, Body()]):
    data = service.create(
        schema=create_schema, plain_password=create_schema.password.get_secret_value()
    )
    return Response(data=data)


@router.get("/{username}", response_model=Response[UserRead], dependencies=[RequireSuperuserDI])
def get_by_username(service: _TenantSuperuserService, username: str):
    return Response(data=service.get_by_username(username))


@router.put(
    "/{username}",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(service: _TenantSuperuserService, username: str, update_schema: UserUpdate):
    return Response(data=service.update(username, update_schema))


@router.patch(
    "/{username}/activate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(service: _TenantSuperuserService, username: str):
    return Response(data=service.activate(username))


@router.patch(
    "/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(service: _TenantSuperuserService, username: str):
    return Response(data=service.deactivate(username))


@router.patch(
    "/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def reset_password(service: _TenantSuperuserService, username: str, schema: ResetPassword):
    return Response(data=service.reset_password(username, schema.new_password.get_secret_value()))


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI]
)
def delete(service: _TenantSuperuserService, username: str):
    service.delete(username)
