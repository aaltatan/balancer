# ruff: noqa: ARG001
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse


def already_exists_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


def authentication_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


def not_found_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )
