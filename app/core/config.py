from typing import Literal

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    APP_NAME: str = "Book Service"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # DataBase
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    DB_ECHO: bool = False

    # Auth
    JWT_SECRET_KEY: SecretStr = SecretStr("change-me")
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = Field(default=15, ge=1)
    REFRESH_TOKEN_TTL_DAYS: int = Field(default=14, ge=1)

    @field_validator("POSTGRES_USER", "POSTGRES_DB", "POSTGRES_HOST")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def secret_required_in_prod(cls, v: SecretStr, info) -> SecretStr:
        if info.data.get("ENVIRONMENT") == "production" and v.get_secret_value() == "change-me":
            raise ValueError("JWT_SECRET_KEY must be set in production!")
        return v

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
