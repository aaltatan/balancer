from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_active_tenant, get_tenant_superuser
from app.db import TenantDB, get_db
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.generic_user import GenericUserService, UserAlreadyExistsError, UserNotFoundError
from app.services.user import UserService

router = APIRouter()


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    tenant: Annotated[TenantDB, Depends(get_active_tenant)],
) -> UserService:
    return UserService(db, GenericUserService(db), tenant)


_UserService = Annotated[UserService, Depends(get_user_service)]


@router.get(
    "/",
    response_model=Response[list[UserRead]],
    dependencies=[Depends(get_tenant_superuser)],
)
def get_all(service: _UserService):
    return Response(data=service.get_all())


@router.post(
    "/",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_tenant_superuser)],
)
def create(service: _UserService, user: UserCreate):
    try:
        data = service.create(
            user.username,
            user.firstname,
            user.lastname,
            user.password.get_secret_value(),
            user.permissions,
        )
        return Response(data=data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get(
    "/{username}",
    response_model=Response[UserRead],
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
)
def reset_password(service: _UserService, username: str, schema: Annotated[ResetPassword, Form()]):
    try:
        data = service.reset_password(username, schema.new_password.get_secret_value())
        return Response(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
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
    dependencies=[Depends(get_tenant_superuser)],
)
def bulk_deactivate(service: _UserService, usernames: Annotated[list[str], Body()]):
    try:
        return Response(data=service.bulk_deactivate(usernames))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
    "/bulk/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_tenant_superuser)],
)
def bulk_delete(service: _UserService, usernames: Annotated[list[str], Body()]):
    try:
        service.bulk_delete(usernames)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
