from sqlalchemy import insert, or_, select
from sqlalchemy.orm import selectinload

from app.models.author import AuthorDB
from app.models.book import BookDB
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BookDB]):
    _model = BookDB

    async def get(self, pk: int) -> BookDB | None:
        stmt = select(BookDB).where(BookDB.id == pk).options(selectinload(BookDB.author))
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def list_books(self, *, filters, sort_field, sort_desc, after_id, limit):
        stmt = select(BookDB).join(BookDB.author).options(selectinload(BookDB.author))
        if filters.title:
            stmt = stmt.where(BookDB.title.ilike(f"%{filters.title}%"))
        if filters.author:
            term = f"%{filters.author}%"
            stmt = stmt.where(or_(AuthorDB.first_name.ilike(term), AuthorDB.last_name.ilike(term)))
        if filters.genre:
            stmt = stmt.where(BookDB.genre == filters.genre)
        if filters.year_from is not None:
            stmt = stmt.where(BookDB.year >= filters.year_from)
        if filters.year_to is not None:
            stmt = stmt.where(BookDB.year <= filters.year_to)
        if after_id is not None:
            stmt = stmt.where(BookDB.id > after_id)
        col = getattr(BookDB, sort_field)
        stmt = stmt.order_by(col.desc() if sort_desc else col.asc(), BookDB.id).limit(limit)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_all(self) -> list[BookDB]:
        stmt = select(BookDB).options(selectinload(BookDB.author)).order_by(BookDB.id)
        return list((await self._session.execute(stmt)).scalars().all())

    async def bulk_create(self, rows: list[dict]) -> None:
        await self._session.execute(insert(BookDB), rows)
        await self._session.flush()
