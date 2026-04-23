from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from balancer.domain.schemas.user import ResetPassword, UserCreate, UserRead, UserUpdate
from balancer.domain.services.generic_user import GenericUserService
from balancer.domain.services.tenant_superuser import TenantSuperuserService
from balancer.entrypoint.api.dependencies.auth import RequireSuperuserDI
from balancer.entrypoint.api.dependencies.db import SessionDI
from balancer.entrypoint.api.dependencies.hash import PWDHasherFnDI
from balancer.entrypoint.api.dependencies.tenant import ActiveTenantDI
from balancer.entrypoint.api.response import ObjectResponse

router = APIRouter()


def get_tenant_superuser_service(
    db: SessionDI, tenant: ActiveTenantDI, hasher_fn: PWDHasherFnDI
) -> TenantSuperuserService:
    return TenantSuperuserService(db, GenericUserService(db, hasher_fn), tenant)


@router.get("/", response_model=list[UserRead], dependencies=[RequireSuperuserDI])
def get_all(service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)]):
    return service.get_all()


@router.post(
    "/",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireSuperuserDI],
)
def create(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    create_schema: Annotated[UserCreate, Body()],
):
    return ObjectResponse(
        item=service.create(
            schema=create_schema, plain_password=create_schema.password.get_secret_value()
        )
    )


@router.get(
    "/{username}", response_model=ObjectResponse[UserRead], dependencies=[RequireSuperuserDI]
)
def get_by_username(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)], username: str
):
    return ObjectResponse(item=service.get_by_username(username))


@router.put(
    "/{username}",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def update(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: str,
    update_schema: UserUpdate,
):
    return ObjectResponse(item=service.update(username, update_schema))


@router.patch(
    "/{username}/activate",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def activate(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)], username: str
):
    return ObjectResponse(item=service.activate(username))


@router.patch(
    "/{username}/deactivate",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def deactivate(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)], username: str
):
    return ObjectResponse(item=service.deactivate(username))


@router.patch(
    "/{username}/reset-password",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireSuperuserDI],
)
def reset_password(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)],
    username: str,
    schema: ResetPassword,
):
    return ObjectResponse(
        item=service.reset_password(username, schema.new_password.get_secret_value())
    )


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI]
)
def delete(
    service: Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)], username: str
):
    service.delete(username)
