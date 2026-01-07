from fastapi import APIRouter

from . import admin, tenants, users

router = APIRouter()

router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(users.router, prefix="/users", tags=["users"])
