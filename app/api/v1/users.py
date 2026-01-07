from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.user import (
    TenantNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserService,
)

router = APIRouter()


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


Service = Annotated[UserService, Depends(get_user_service)]


@router.get("/{tenant_slug}/users", response_model=list[UserRead])
def get_users(service: Service, tenant_slug: str):
    try:
        return service.get_all(tenant_slug)
    except TenantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.post(
    "/{tenant_slug}/tenant-user",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant_user(service: Service, user: UserCreate, tenant_slug: str):
    try:
        return service.create_tenant_user(tenant_slug, user, user.password.get_secret_value())
    except (UserAlreadyExistsError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{tenant_slug}/users/{username}", response_model=UserRead)
def get_user(service: Service, username: str, tenant_slug: str):
    try:
        return service.get_by_username(tenant_slug, username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{tenant_slug}/{username}",
    response_model=UserRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_user(service: Service, username: str, user: UserUpdate, tenant_slug: str):
    try:
        return service.update(tenant_slug, username, user)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/activate",
    response_model=UserRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def activate_user(service: Service, username: str, tenant_slug: str):
    try:
        return service.activate(tenant_slug, username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/deactivate",
    response_model=UserRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def deactivate_user(service: Service, username: str, tenant_slug: str):
    try:
        return service.deactivate(tenant_slug, username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/{username}/reset-password",
    response_model=UserRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def reset_password(
    service: Service, username: str, schema: Annotated[ResetPassword, Form()], tenant_slug: str
):
    try:
        return service.reset_password(tenant_slug, username, schema.new_password.get_secret_value())
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{tenant_slug}/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(service: Service, username: str, tenant_slug: str):
    try:
        service.delete(tenant_slug, username)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/bulk/activate",
    response_model=list[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_activate_users(
    service: Service, usernames: Annotated[list[str], Body()], tenant_slug: str
):
    try:
        return service.bulk_activate(tenant_slug, usernames)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{tenant_slug}/bulk/deactivate",
    response_model=list[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_deactivate_users(
    service: Service, usernames: Annotated[list[str], Body()], tenant_slug: str
):
    try:
        return service.bulk_deactivate(tenant_slug, usernames)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch("/{tenant_slug}/bulk/delete", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_users(service: Service, usernames: Annotated[list[str], Body()], tenant_slug: str):
    try:
        service.bulk_delete(tenant_slug, usernames)
    except (UserNotFoundError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
