from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import DBSession
from app.schemas.book import (
    CURRENT_YEAR,
    BookCreate,
    BookFilter,
    BookRead,
    BookUpdate,
    Genre,
    SortField,
)
from app.services.book_service import BookService

router = APIRouter()


def get_book_service(session: DBSession) -> BookService:
    return BookService(session)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(body: BookCreate, service: BookServiceDep) -> BookRead:
    return await service.create_book(body)


@router.get("/", response_model=list[BookRead])
async def list_books(
    service: BookServiceDep,
    title: str | None = None,
    author: str | None = None,
    genre: Genre | None = None,
    year_from: int | None = Query(default=None, ge=1800),
    year_to: int | None = Query(default=None, le=CURRENT_YEAR),
    sort: SortField = SortField.id,
    desc: bool = False,
    after_id: int | None = Query(default=None, description="keyset cursor: id останньої книги попередньої сторінки"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[BookRead]:
    filters = BookFilter(title=title, author=author, genre=genre, year_from=year_from, year_to=year_to)
    return await service.list_books(filters=filters, sort_field=sort, sort_desc=desc, after_id=after_id, limit=limit)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, service: BookServiceDep) -> BookRead:
    return await service.get_book(book_id)


@router.patch("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, body: BookUpdate, service: BookServiceDep) -> BookRead:
    return await service.update_book(book_id, body)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    await service.delete_book(book_id)
