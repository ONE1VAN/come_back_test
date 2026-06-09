import csv
import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import DBSession, get_current_user_id
from app.schemas.book import BookCreate, BookListParams, BookRead, BookUpdate, BulkResult
from app.services.book_service import BookService

router = APIRouter()
write_router = APIRouter(dependencies=[Depends(get_current_user_id)])


def get_book_service(session: DBSession) -> BookService:
    return BookService(session)


BookServiceDep = Annotated[BookService, Depends(get_book_service)]


def _csv_to_nested(raw: dict) -> dict:
    return {
        "title": raw.get("title"),
        "genre": raw.get("genre"),
        "year": raw.get("year"),
        "author": {
            "first_name": raw.get("author_first_name"),
            "last_name": raw.get("author_last_name"),
            "birth_year": raw.get("author_birth_year") or None,
            "death_year": raw.get("author_death_year") or None,
        },
    }


@router.get("/", response_model=list[BookRead])
async def list_books(service: BookServiceDep, params: Annotated[BookListParams, Query()]) -> list[BookRead]:
    return await service.list_books(params)


@router.get("/export")
async def export_books(service: BookServiceDep, format: Annotated[str, Query(pattern="^(json|csv)$")] = "json"):
    books = await service.export_books()
    if format == "csv":

        def gen():
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow(["id", "title", "author_first_name", "author_last_name", "genre", "year"])
            for b in books:
                writer.writerow([b.id, b.title, b.author.first_name, b.author.last_name, b.genre, b.year])
            yield buf.getvalue()

        return StreamingResponse(
            gen(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=books.csv"},
        )
    return books


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, service: BookServiceDep) -> BookRead:
    return await service.get_book(book_id)


@write_router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(body: BookCreate, service: BookServiceDep) -> BookRead:
    return await service.create_book(body)


@write_router.post("/bulk", response_model=BulkResult)
async def bulk_import(service: BookServiceDep, file: Annotated[UploadFile, File()]) -> BulkResult:
    content = (await file.read()).decode("utf-8")
    if file.filename and file.filename.endswith(".csv"):
        rows = [_csv_to_nested(r) for r in csv.DictReader(io.StringIO(content))]
    else:
        rows = json.loads(content)
    return await service.bulk_import(rows)


@write_router.patch("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, body: BookUpdate, service: BookServiceDep) -> BookRead:
    return await service.update_book(book_id, body)


@write_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    await service.delete_book(book_id)
