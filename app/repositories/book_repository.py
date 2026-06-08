from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.book import BookDB
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BookDB]):
    _model = BookDB

    async def get(self, pk: int) -> BookDB | None:
        # Підвантажуємо автора одразу: в async ліниве завантаження book.author заборонене.
        stmt = select(BookDB).where(BookDB.id == pk).options(selectinload(BookDB.author))
        return (await self._session.execute(stmt)).scalar_one_or_none()
