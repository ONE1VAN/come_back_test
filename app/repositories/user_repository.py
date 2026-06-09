from sqlalchemy import select

from app.models.users import UserDB
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserDB]):
    _model = UserDB

    async def get_by_email(self, email: str) -> UserDB | None:
        res = await self._session.execute(select(UserDB).where(UserDB.email == email))
        return res.scalar_one_or_none()
