from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import auth, v1
from app.core.config import get_config
from app.core.exception_handlers import (
    bad_request_400_error_handler,
    conflict_409_error_handler,
    not_found_404_error_handler,
)
from app.core.middlewares import profiler_middleware
from app.db import SessionLocal, init_db
from app.db.permission import init_permissions
from app.exceptions import (
    AlreadyExistsError,
    BulkNotFoundError,
    CannotDeleteError,
    InvalidPasswordError,
    NotFoundError,
    UserAlreadyExistsError,
)


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

app.add_exception_handler(AlreadyExistsError, conflict_409_error_handler)
app.add_exception_handler(InvalidPasswordError, bad_request_400_error_handler)
app.add_exception_handler(NotFoundError, not_found_404_error_handler)
app.add_exception_handler(CannotDeleteError, conflict_409_error_handler)
app.add_exception_handler(BulkNotFoundError, not_found_404_error_handler)
app.add_exception_handler(UserAlreadyExistsError, conflict_409_error_handler)

# routers

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(v1.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
