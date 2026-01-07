from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Response
from app.models.user import UserCreate, UserRead
from app.services.user import TenantNotFoundError, UserAlreadyExistsError, UserService

router = APIRouter()


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


Service = Annotated[UserService, Depends(get_user_service)]


@router.post(
    "{tenant_slug}/tenant-superuser",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def create_tenant_superuser(service: Service, user: UserCreate, tenant_slug: str):
    try:
        data = service.create_tenant_superuser(tenant_slug, user, user.password.get_secret_value())
        return Response(data=data)
    except (UserAlreadyExistsError, TenantNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
