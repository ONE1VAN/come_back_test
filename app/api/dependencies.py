from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import decode_token
from app.exceptions.base import UnauthorizedException

DBSession = Annotated[AsyncSession, Depends(get_session)]

_bearer = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> int:
    if creds is None:
        raise UnauthorizedException("Missing authorization header")
    payload = decode_token(creds.credentials)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")
    user_id = int(payload["sub"])
    request.state.user = str(user_id)
    return user_id


CurrentUser = Annotated[int, Depends(get_current_user_id)]
