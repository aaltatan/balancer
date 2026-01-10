from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status

from app.api.dependencies.auth import ActiveTenantDI, RequireTenantSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.generic_user import GenericUserService, UserAlreadyExistsError, UserNotFoundError
from app.services.user import UserService

router = APIRouter()


def get_user_service(db: SessionDI, tenant: ActiveTenantDI) -> UserService:
    return UserService(db, GenericUserService(db), tenant)


_UserService = Annotated[UserService, Depends(get_user_service)]


@router.get("/", response_model=Response[list[UserRead]], dependencies=[RequireTenantSuperuserDI])
def get_all(service: _UserService):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequireTenantSuperuserDI],
)
def create(service: _UserService, user: UserCreate, hasher_fn: PWDHasherFnDI):
    try:
        data = service.create(
            user.username,
            user.firstname,
            user.lastname,
            user.password.get_secret_value(),
            user.permissions,
            hasher_fn=hasher_fn,
        )
        return Response(data=data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get(
    "/{username}", response_model=Response[UserRead], dependencies=[RequireTenantSuperuserDI]
)
def get_by_username(service: _UserService, username: str):
    try:
        return Response(data=service.get_by_username(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{username}",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def update(service: _UserService, username: str, user: UserUpdate):
    try:
        return Response(data=service.update(username, user.firstname, user.lastname))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/activate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def activate(service: _UserService, username: str):
    try:
        return Response(data=service.activate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def deactivate(service: _UserService, username: str):
    try:
        return Response(data=service.deactivate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def reset_password(
    service: _UserService,
    username: str,
    schema: Annotated[ResetPassword, Form()],
    hasher_fn: PWDHasherFnDI,
):
    try:
        data = service.reset_password(
            username, schema.new_password.get_secret_value(), hasher_fn=hasher_fn
        )
        return Response(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireTenantSuperuserDI]
)
def delete(service: _UserService, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/bulk/activate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def bulk_activate(service: _UserService, usernames: Annotated[list[str], Body()]):
    try:
        return Response(data=service.bulk_activate(usernames))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/bulk/deactivate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[RequireTenantSuperuserDI],
)
def bulk_deactivate(service: _UserService, usernames: Annotated[list[str], Body()]):
    try:
        return Response(data=service.bulk_deactivate(usernames))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
    "/bulk/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireTenantSuperuserDI]
)
def bulk_delete(service: _UserService, usernames: Annotated[list[str], Body()]):
    try:
        service.bulk_delete(usernames)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
