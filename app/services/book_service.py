from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundException
from app.models.author import AuthorDB
from app.models.book import BookDB
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.schemas.author import AuthorRead
from app.schemas.book import BookCreate, BookFilter, BookListParams, BookRead, BookUpdate
from app.services.base import BaseService


class BookService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._books = BookRepository(session)
        self._authors = AuthorRepository(session)

    @staticmethod
    def _to_read(book: BookDB, author: AuthorDB) -> BookRead:
        return BookRead(
            id=book.id,
            title=book.title,
            genre=book.genre,
            year=book.year,
            author=AuthorRead(
                id=author.id,
                first_name=author.first_name,
                last_name=author.last_name,
                birth_year=author.birth_year,
                death_year=author.death_year,
            ),
        )

    async def create_book(self, data: BookCreate) -> BookRead:
        author = await self._authors.get_or_create(data.author.model_dump())
        book = await self._books.create(
            {"title": data.title, "author_id": author.id, "genre": data.genre, "year": data.year}
        )
        await self._session.commit()
        return self._to_read(book, author)

    async def get_book(self, book_id: int) -> BookRead:
        book = await self._books.get(book_id)
        if book is None:
            raise NotFoundException(f"Book id={book_id} not found")
        return self._to_read(book, book.author)

    async def update_book(self, book_id: int, data: BookUpdate) -> BookRead:
        if not await self._books.exists(id=book_id):
            raise NotFoundException(f"Book id={book_id} not found")
        patch = data.model_dump(exclude_unset=True)
        if "author" in patch:
            author = await self._authors.get_or_create(patch.pop("author"))
            patch["author_id"] = author.id
        book = await self._books.update(book_id, patch)
        await self._session.commit()
        return self._to_read(book, book.author)

    async def delete_book(self, book_id: int) -> None:
        if not await self._books.delete(book_id):
            raise NotFoundException(f"Book id={book_id} not found")
        await self._session.commit()

    async def list_books(self, params: BookListParams) -> list[BookRead]:
        filters = BookFilter(
            title=params.title,
            author=params.author,
            genre=params.genre,
            year_from=params.year_from,
            year_to=params.year_to,
        )
        books = await self._books.list_books(
            filters=filters,
            sort_field=params.sort,
            sort_desc=params.desc,
            after_id=params.after_id,
            limit=params.limit,
        )
        return [self._to_read(b, b.author) for b in books]
