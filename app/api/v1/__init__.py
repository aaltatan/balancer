from fastapi import APIRouter

from . import tenant_superusers, tenants, users

# v1 main router
router = APIRouter()
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])

# v1 tenant router
tenant_router = APIRouter()
tenant_router.include_router(
    tenant_superusers.router, prefix="/tenant-superusers", tags=["Tenant Superusers"]
)
tenant_router.include_router(users.router, prefix="/users", tags=["users"])

# v1 router
router.include_router(tenant_router, prefix="/{tenant_code}")
