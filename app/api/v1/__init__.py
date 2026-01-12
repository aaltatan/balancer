from fastapi import APIRouter

from . import tenant_superusers, tenants, users

router = APIRouter()

router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(
    tenant_superusers.router, prefix="{tenant_slug}/tenant-superusers", tags=["Tenant Superusers"]
)
router.include_router(users.router, prefix="/{tenant_slug}/users", tags=["users"])
