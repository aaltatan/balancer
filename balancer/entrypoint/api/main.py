from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from balancer.config import get_config
from balancer.domain.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    CannotDeleteError,
    NotFoundError,
)
from balancer.domain.models import SessionLocal, init_db
from balancer.domain.models.permission import init_permissions

from .exception_handlers import (
    already_exists_error_handler,
    authentication_error_handler,
    cannot_delete_error_handler,
    not_found_error_handler,
)
from .middlewares import profiler_middleware
from .routers import auth, v1


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    with SessionLocal() as session:
        init_db()
        init_permissions(session)

    yield


config = get_config()
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description=config.app_description,
    lifespan=lifespan,
)

# middlewares

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.debug:
    app.add_middleware(BaseHTTPMiddleware, dispatch=profiler_middleware)

# exception handlers

app.add_exception_handler(AlreadyExistsError, already_exists_error_handler)
app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)
app.add_exception_handler(CannotDeleteError, cannot_delete_error_handler)

# routers

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(v1.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
