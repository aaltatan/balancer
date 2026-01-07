from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.tenant import get_current_tenant
from app.db import get_db
from app.db.tenant import TenantDB
from app.models import Response
from app.models.user import UserCreate, UserRead
from app.services.user import UserAlreadyExistsError, UserService

router = APIRouter()


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    tenant: Annotated[TenantDB, Depends(get_current_tenant)],
) -> UserService:
    return UserService(db, tenant)


Service = Annotated[UserService, Depends(get_user_service)]


@router.post("/", response_model=Response[UserRead], status_code=status.HTTP_201_CREATED)
def create_tenant_superuser(service: Service, user: UserCreate):
    try:
        data = service.create_tenant_superuser(user, user.password.get_secret_value())
        return Response(data=data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
