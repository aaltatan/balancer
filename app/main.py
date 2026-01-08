from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import v1
from app.core.config import get_config
from app.core.middlewares import profiler_middleware
from app.db import SessionLocal, init_db
from app.db.permission import init_permissions


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.debug:
    app.add_middleware(BaseHTTPMiddleware, dispatch=profiler_middleware)

app.include_router(v1.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
