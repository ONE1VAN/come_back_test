from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseDB

ModelT = TypeVar("ModelT", bound=BaseDB)


class BaseRepository(Generic[ModelT]):
    _model: ClassVar[type]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _pk(self):
        return sa_inspect(self._model).mapper.primary_key[0]

    async def get(self, pk: Any) -> ModelT | None:
        res = await self._session.execute(select(self._model).where(self._pk() == pk))
        return res.scalar_one_or_none()

    async def create(self, data: dict) -> ModelT:
        instance = self._model(**data)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, pk: Any, data: dict) -> ModelT | None:
        await self._session.execute(update(self._model).where(self._pk() == pk).values(**data))
        await self._session.flush()
        return await self.get(pk)

    async def delete(self, pk: Any) -> bool:
        res = await self._session.execute(delete(self._model).where(self._pk() == pk))
        return res.rowcount > 0

    async def exists(self, **filters: Any) -> bool:
        stmt = select(self._model.id).limit(1)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self._model, attr) == value)
        return (await self._session.execute(stmt)).first() is not None
