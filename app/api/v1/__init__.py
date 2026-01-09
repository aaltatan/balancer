from fastapi import APIRouter

from . import superuser, tenants, users

router = APIRouter()

router.include_router(superuser.router, prefix="/{tenant_slug}/superusers", tags=["superusers"])
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(users.router, prefix="/{tenant_slug}/users", tags=["users"])
