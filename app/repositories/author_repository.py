from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.author import AuthorDB
from app.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[AuthorDB]):
    _model = AuthorDB

    async def get_or_create(self, data: dict) -> AuthorDB:
        ident = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "birth_year": data.get("birth_year"),
        }
        stmt = (
            pg_insert(AuthorDB)
            .values(**data)
            .on_conflict_do_nothing(index_elements=["first_name", "last_name", "birth_year"])
            .returning(AuthorDB.id)
        )
        res = await self._session.execute(stmt)
        author_id = res.scalar_one_or_none()
        if author_id is None:
            res = await self._session.execute(
                select(AuthorDB).where(
                    AuthorDB.first_name == ident["first_name"],
                    AuthorDB.last_name == ident["last_name"],
                    AuthorDB.birth_year.is_not_distinct_from(ident["birth_year"]),
                )
            )
            return res.scalar_one()
        await self._session.flush()
        return await self.get(author_id)
