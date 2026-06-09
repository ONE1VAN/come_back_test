from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import DBSession
from app.schemas.auth import LoginIn, RefreshIn, RegisterIn, TokenPair
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(session: DBSession) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, service: AuthServiceDep) -> TokenPair:
    return await service.register(body)


@router.post("/login", response_model=TokenPair)
async def login(body: LoginIn, service: AuthServiceDep) -> TokenPair:
    return await service.login(body)


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshIn, service: AuthServiceDep) -> TokenPair:
    return await service.refresh(body.refresh_token)
