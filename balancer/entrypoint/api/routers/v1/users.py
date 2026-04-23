from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, status

from balancer.domain.schemas.user import ResetPassword, UserCreate, UserRead, UserUpdate
from balancer.domain.services.generic_user import GenericUserService
from balancer.domain.services.user import UserService
from balancer.entrypoint.api.dependencies.auth import RequireAnySuperuserDI
from balancer.entrypoint.api.dependencies.db import SessionDI
from balancer.entrypoint.api.dependencies.hash import PWDHasherFnDI
from balancer.entrypoint.api.dependencies.tenant import ActiveTenantDI
from balancer.entrypoint.api.response import ObjectResponse

router = APIRouter()


def get_user_service(
    db: SessionDI, tenant: ActiveTenantDI, hasher_fn: PWDHasherFnDI
) -> UserService:
    return UserService(db, GenericUserService(db, hasher_fn), tenant)


@router.get("/", response_model=list[UserRead], dependencies=[RequireAnySuperuserDI])
def get_all(service: Annotated[UserService, Depends(get_user_service)]):
    return service.get_all()


@router.post(
    "/",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAnySuperuserDI],
)
def create(service: Annotated[UserService, Depends(get_user_service)], create_schema: UserCreate):
    return ObjectResponse(
        item=service.create(
            schema=create_schema, plain_password=create_schema.password.get_secret_value()
        )
    )


@router.get(
    "/{username}", response_model=ObjectResponse[UserRead], dependencies=[RequireAnySuperuserDI]
)
def get_by_username(service: Annotated[UserService, Depends(get_user_service)], username: str):
    return ObjectResponse(item=service.get_by_username(username))


@router.put(
    "/{username}",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def update(
    service: Annotated[UserService, Depends(get_user_service)],
    username: str,
    update_schema: UserUpdate,
):
    return ObjectResponse(item=service.update(username, update_schema))


@router.patch(
    "/{username}/activate",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def activate(service: Annotated[UserService, Depends(get_user_service)], username: str):
    return ObjectResponse(item=service.activate(username))


@router.patch(
    "/{username}/deactivate",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def deactivate(service: Annotated[UserService, Depends(get_user_service)], username: str):
    return ObjectResponse(item=service.deactivate(username))


@router.patch(
    "/{username}/reset-password",
    response_model=ObjectResponse[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def reset_password(
    service: Annotated[UserService, Depends(get_user_service)],
    username: str,
    schema: Annotated[ResetPassword, Form()],
):
    return ObjectResponse(
        item=service.reset_password(username, schema.new_password.get_secret_value())
    )


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def delete(service: Annotated[UserService, Depends(get_user_service)], username: str):
    service.delete(username)


@router.patch(
    "/bulk/activate",
    response_model=ObjectResponse[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_activate(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    return ObjectResponse(item=service.bulk_activate(usernames))


@router.patch(
    "/bulk/deactivate",
    response_model=ObjectResponse[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_deactivate(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    return ObjectResponse(item=service.bulk_deactivate(usernames))


@router.delete(
    "/bulk/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def bulk_delete(
    service: Annotated[UserService, Depends(get_user_service)],
    usernames: Annotated[list[str], Body()],
):
    service.bulk_delete(usernames)
