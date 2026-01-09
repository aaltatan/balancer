from fastapi import APIRouter

from . import superusers, tenants, users

router = APIRouter()

router.include_router(superusers.router, prefix="/superusers", tags=["superusers"])
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(users.router, prefix="/users", tags=["users"])
