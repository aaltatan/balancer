from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
<<<<<<< HEAD

from app.api.dependencies.auth import RequireSuperuserDI
from app.api.dependencies.db import SessionDI
from app.api.dependencies.hash import PWDHasherFnDI
=======
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_superuser
from app.db import get_db
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
from app.models import Response
from app.models.user import ResetPassword, UserCreate, UserRead, UserUpdate
from app.services.generic_user import (
    GenericUserService,
    MoreThanOneSuperuserError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.services.tenant_superuser import TenantSuperuserService

router = APIRouter()


<<<<<<< HEAD
def get_tenant_superuser_service(db: SessionDI) -> TenantSuperuserService:
=======
def get_tenant_superuser_service(db: Annotated[Session, Depends(get_db)]) -> TenantSuperuserService:
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
    return TenantSuperuserService(db, GenericUserService(db))


_TenantSuperuserService = Annotated[TenantSuperuserService, Depends(get_tenant_superuser_service)]


<<<<<<< HEAD
@router.get("/", response_model=Response[list[UserRead]], dependencies=[RequireSuperuserDI])
=======
@router.get(
    "/",
    response_model=Response[list[UserRead]],
    dependencies=[Depends(get_superuser)],
)
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
def get_all(service: _TenantSuperuserService):
    return Response(data=service.get_all())


@router.post(
    "/{tenant_slug}",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
=======
    dependencies=[Depends(get_superuser)],
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
)
def create(
    service: _TenantSuperuserService,
    user: Annotated[UserCreate, Body()],
    tenant_slug: Annotated[str, Path()],
<<<<<<< HEAD
    hasher_fn: PWDHasherFnDI,
=======
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
):
    try:
        data = service.create(
            user.username,
            user.firstname,
            user.lastname,
            user.password.get_secret_value(),
            tenant_slug,
<<<<<<< HEAD
            hasher_fn=hasher_fn,
=======
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
        )
        return Response(data=data)
    except (UserAlreadyExistsError, MoreThanOneSuperuserError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None


<<<<<<< HEAD
@router.get("/{username}", response_model=Response[UserRead], dependencies=[RequireSuperuserDI])
=======
@router.get(
    "/{username}",
    response_model=Response[UserRead],
    dependencies=[Depends(get_superuser)],
)
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
def get_by_username(service: _TenantSuperuserService, username: str):
    try:
        return Response(data=service.get_by_username(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.put(
    "/{username}",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
=======
    dependencies=[Depends(get_superuser)],
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
)
def update(service: _TenantSuperuserService, username: str, user: UserUpdate):
    try:
        return Response(data=service.update(username, user.firstname, user.lastname))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/activate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
=======
    dependencies=[Depends(get_superuser)],
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
)
def activate(service: _TenantSuperuserService, username: str):
    try:
        return Response(data=service.activate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/deactivate",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
=======
    dependencies=[Depends(get_superuser)],
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
)
def deactivate(service: _TenantSuperuserService, username: str):
    try:
        return Response(data=service.deactivate(username))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.patch(
    "/{username}/reset-password",
    response_model=Response[UserRead],
    status_code=status.HTTP_202_ACCEPTED,
<<<<<<< HEAD
    dependencies=[RequireSuperuserDI],
)
def reset_password(
    service: _TenantSuperuserService, username: str, schema: ResetPassword, hasher_fn: PWDHasherFnDI
):
    try:
        data = service.reset_password(
            username, schema.new_password.get_secret_value(), hasher_fn=hasher_fn
        )
=======
    dependencies=[Depends(get_superuser)],
)
def reset_password(service: _TenantSuperuserService, username: str, schema: ResetPassword):
    try:
        data = service.reset_password(username, schema.new_password.get_secret_value())
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
        return Response(data=data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None


@router.delete(
<<<<<<< HEAD
    "/{username}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[RequireSuperuserDI]
=======
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_superuser)],
>>>>>>> 8c9d9914ef549923d3df8012e10d83a1987b8225
)
def delete(service: _TenantSuperuserService, username: str):
    try:
        service.delete(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
