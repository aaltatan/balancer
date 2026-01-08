from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.tenant import get_current_tenant
from app.db import TenantDB, get_db
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.user import UserAlreadyExistsError, UserNotFoundError, UserService

router = APIRouter()


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    tenant: Annotated[TenantDB, Depends(get_current_tenant)],
) -> UserService:
    return UserService(db, tenant)


Service = Annotated[UserService, Depends(get_user_service)]


@router.get("/", response_model=Response[list[UserRead]])
def get_users(service: Service):
    return Response(data=service.get_all())


@router.post("/", response_model=Response[UserRead], status_code=status.HTTP_201_CREATED)
def create_tenant_user(service: Service, user: UserCreate):
    try:
        data = service.create_tenant_user(user, user.password.get_secret_value())
        return Response(data=data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{username}", response_model=Response[UserRead])
def get_user(service: Service, username: str):
    try:
        return Response(data=service.get_by_username(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put("/{username}", response_model=Response[UserRead], status_code=status.HTTP_202_ACCEPTED)
def update_user(service: Service, username: str, user: UserUpdate):
    try:
        return Response(data=service.update(username, user))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/activate", response_model=Response[UserRead], status_code=status.HTTP_202_ACCEPTED
)
def activate_user(service: Service, username: str):
    try:
        return Response(data=service.activate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def deactivate_user(service: Service, username: str):
    try:
        return Response(data=service.deactivate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
)
def reset_password(service: Service, username: str, schema: Annotated[ResetPassword, Form()]):
    try:
        data = service.reset_password(username, schema.new_password.get_secret_value())
        return Response(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(service: Service, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/bulk/activate", response_model=Response[list[UserRead]], status_code=status.HTTP_202_ACCEPTED
)
def bulk_activate_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        return Response(data=service.bulk_activate(usernames))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/bulk/deactivate",
    response_model=Response[list[UserRead]],
    status_code=status.HTTP_202_ACCEPTED,
)
def bulk_deactivate_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        return Response(data=service.bulk_deactivate(usernames))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/bulk/delete", status_code=status.HTTP_204_NO_CONTENT)
def bulk_delete_users(service: Service, usernames: Annotated[list[str], Body()]):
    try:
        service.bulk_delete(usernames)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
