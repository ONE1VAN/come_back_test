from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions.base import ConflictException, UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginIn, RegisterIn, TokenPair
from app.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._users = UserRepository(session)

    def _issue(self, user_id: int) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def register(self, data: RegisterIn) -> TokenPair:
        if await self._users.get_by_email(data.email):
            raise ConflictException("Email already registered")
        user = await self._users.create(
            {
                "username": data.username,
                "email": data.email,
                "password_hash": hash_password(data.password),
            }
        )
        await self._session.commit()
        return self._issue(user.id)

    async def login(self, data: LoginIn) -> TokenPair:
        user = await self._users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid credentials")
        return self._issue(user.id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
        return self._issue(int(payload["sub"]))
