from fastapi import APIRouter

from app.api.v1.endpoints import auth, books, health

v1_router = APIRouter()
v1_router.include_router(health.router, prefix="/health", tags=["Health"])
v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
v1_router.include_router(books.router, prefix="/books", tags=["Books"])
v1_router.include_router(books.write_router, prefix="/books", tags=["Books"])
