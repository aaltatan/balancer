from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db import TenantDB, get_db
from app.dependencies.tenant import get_current_tenant
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.user import (
    TenantNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)

router = APIRouter()


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    tenant: Annotated[TenantDB, Depends(get_current_tenant)],
) -> UserService:
    return UserService(db, tenant)


Service = Annotated[UserService, Depends(get_user_service)]


@router.get("/{tenant_slug}/users", response_model=Response[list[UserRead]])
def get_users(service: Service):
    try:
        return Response(data=service.get_all())
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.post(
    "/{tenant_slug}/tenant-user",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def create_tenant_user(service: Service, user: UserCreate):
    try:
        data = service.create_tenant_user(user, user.password.get_secret_value())
        return Response(data=data)
    except (UserAlreadyExistsError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{tenant_slug}/users/{username}", response_model=Response[UserRead])
def get_user(service: Service, username: str):
    try:
        return service.get_by_username(username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{tenant_slug}/{username}",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def update_user(service: Service, username: str, user: UserUpdate):
    try:
        data = service.update(username, user)
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/activate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def activate_user(service: Service, username: str):
    try:
        data = service.activate(username)
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def deactivate_user(service: Service, username: str):
    try:
        data = service.deactivate(username)
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def reset_password(service: Service, username: str, schema: Annotated[ResetPassword, Form()]):
    try:
        data = service.reset_password(username, schema.new_password.get_secret_value())
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{tenant_slug}/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(service: Service, username: str):
    try:
        service.delete(username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/bulk/activate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_activate_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.bulk_activate(usernames)
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/bulk/deactivate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_deactivate_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        data = service.bulk_deactivate(usernames)
        return Response(data=data)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch("/{tenant_slug}/bulk/delete", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        service.bulk_delete(usernames)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
