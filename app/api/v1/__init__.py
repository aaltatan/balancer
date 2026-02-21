from fastapi import APIRouter

from . import tenant_superusers, tenants, users

# v1 main router
router = APIRouter()
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(
    tenant_superusers.router, prefix="/tenant-superusers", tags=["tenant-superusers"]
)
router.include_router(users.router, prefix="/users", tags=["users"])
