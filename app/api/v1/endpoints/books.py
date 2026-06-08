from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import DBSession
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services.book_service import BookService

router = APIRouter()


def get_book_service(session: DBSession) -> BookService:
    return BookService(session)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(body: BookCreate, service: BookServiceDep) -> BookRead:
    return await service.create_book(body)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, service: BookServiceDep) -> BookRead:
    return await service.get_book(book_id)


@router.patch("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, body: BookUpdate, service: BookServiceDep) -> BookRead:
    return await service.update_book(book_id, body)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    await service.delete_book(book_id)
