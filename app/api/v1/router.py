from fastapi import APIRouter

from app.api.v1.endpoints import books, health  # auth додамо пізніше

v1_router = APIRouter()
v1_router.include_router(health.router, prefix="/health", tags=["Health"])
v1_router.include_router(books.router, prefix="/books", tags=["Books"])
