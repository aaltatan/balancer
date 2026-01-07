from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Wrapper
from app.models.user import UserCreate, UserRead, UserUpdate
from app.services.user import UserAlreadyExistsError, UserNotFoundError, UserService

router = APIRouter()


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


Service = Annotated[UserService, Depends(get_user_service)]


@router.get("/", response_model=Wrapper[list[UserRead]])
def get_users(service: Service):
    return Wrapper(data=service.get_all())


@router.post("/", response_model=Wrapper[UserRead])
def create_tenant_superuser(service: Service, user: UserCreate):
    try:
        return Wrapper(data=service.create_superuser(user))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


@router.get("/{username}", response_model=Wrapper[UserRead])
def get_user(service: Service, username: str):
    try:
        return Wrapper(data=service.get_by_username(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put("/{username}", response_model=Wrapper[UserRead])
def update_user(service: Service, username: str, user: UserUpdate):
    try:
        return Wrapper(data=service.update(username, user))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete("/{username}", response_model=Wrapper[None])
def delete_user(service: Service, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
