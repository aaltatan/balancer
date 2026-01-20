# ruff: noqa: ARG001
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse


def conflict_409_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


def bad_request_400_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


def not_found_404_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
