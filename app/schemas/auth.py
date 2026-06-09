from pydantic import EmailStr, Field

from app.schemas.base import BasePydanticModel


class RegisterIn(BasePydanticModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginIn(BasePydanticModel):
    email: EmailStr
    password: str


class TokenPair(BasePydanticModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BasePydanticModel):
    refresh_token: str
