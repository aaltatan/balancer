from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, status

from app.api.dependencies.auth import RequireAnySuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI
from app.api.dependencies.tenant import ActiveTenantDI
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.generic_user import GenericUserService
from app.services.user import UserService

router = APIRouter()


def get_user_service(
    db: SessionDI, tenant: ActiveTenantDI, hasher_fn: PWDHasherFnDI
) -> UserService:
    return UserService(db, GenericUserService(db, hasher_fn), tenant)


_UserService = Annotated[UserService, Depends(get_user_service)]


@router.get("/", response_model=Response[list[UserRead]], dependencies=[RequireAnySuperuserDI])
def get_all(service: _UserService):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireAnySuperuserDI],
)
def create(service: _UserService, create_schema: UserCreate):
    data = service.create(
        schema=create_schema, plain_password=create_schema.password.get_secret_value()
    )
    return Response(data=data)


@router.get("/{username}", response_model=Response[UserRead], dependencies=[RequireAnySuperuserDI])
def get_by_username(service: _UserService, username: str):
    return Response(data=service.get_by_username(username))


@router.put(
    "/{username}",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def update(service: _UserService, username: str, update_schema: UserUpdate):
    return Response(data=service.update(username, update_schema))


@router.patch(
    "/{username}/activate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def activate(service: _UserService, username: str):
    return Response(data=service.activate(username))


@router.patch(
    "/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def deactivate(service: _UserService, username: str):
    return Response(data=service.deactivate(username))


@router.patch(
    "/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def reset_password(service: _UserService, username: str, schema: Annotated[ResetPassword, Form()]):
    return Response(data=service.reset_password(username, schema.new_password.get_secret_value()))


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def delete(service: _UserService, username: str):
    service.delete(username)


@router.patch(
    "/bulk/activate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_activate(service: _UserService, usernames: Annotated[list[str], Body()]):
    return Response(data=service.bulk_activate(usernames))


@router.patch(
    "/bulk/deactivate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireAnySuperuserDI],
)
def bulk_deactivate(service: _UserService, usernames: Annotated[list[str], Body()]):
    return Response(data=service.bulk_deactivate(usernames))


@router.delete(
    "/bulk/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireAnySuperuserDI]
)
def bulk_delete(service: _UserService, usernames: Annotated[list[str], Body()]):
    service.bulk_delete(usernames)
