import logging

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.exceptions.base import AppException

logger = logging.getLogger("app")


def _ctx(request: Request) -> tuple[str, str, str]:
    return (
        request.url.path,
        getattr(request.state, "user", "anonymous"),
        getattr(request.state, "request_id", "-"),
    )


def _map_low_level(exc: Exception) -> tuple[int, str]:
    if isinstance(exc, IntegrityError):
        return status.HTTP_409_CONFLICT, "Resource already exists"
    if isinstance(exc, OperationalError):
        return status.HTTP_503_SERVICE_UNAVAILABLE, "Database temporarily unavailable"
    if isinstance(exc, SQLAlchemyError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error"
    if isinstance(exc, ValueError | KeyError):
        return status.HTTP_422_UNPROCESSABLE_CONTENT, "Invalid input"
    return status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    endpoint, user, rid = _ctx(request)
    logger.warning("%s - %s - %s - %s: %s", user, endpoint, exc.status_code, type(exc).__name__, exc.detail)
    body = {"detail": exc.detail, "request_id": rid}
    if getattr(exc, "errors", None):
        body["errors"] = exc.errors
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(body))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    endpoint, user, rid = _ctx(request)
    status_code, client_detail = _map_low_level(exc)
    log = logger.exception if status_code >= 500 else logger.error
    log("%s - %s - %s - %s: %s", user, endpoint, status_code, type(exc).__name__, exc)
    return JSONResponse(status_code=status_code, content={"detail": client_detail, "request_id": rid})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    endpoint, user, rid = _ctx(request)
    logger.warning("%s - %s - 422 - RequestValidationError", user, endpoint)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder({"detail": "Validation error", "errors": exc.errors(), "request_id": rid}),
    )
