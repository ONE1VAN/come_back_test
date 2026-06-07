from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.base import AppException
from app.exceptions.handlers import app_exception_handler, unhandled_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/v1/docs",
    redoc_url=f"{settings.API_PREFIX}/v1/redoc",
    openapi_url=f"{settings.API_PREFIX}/v1/openapi.json",
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
