from pydantic import Field, field_validator, model_validator

from app.schemas.base import BasePydanticModel


class AuthorIn(BasePydanticModel):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    birth_year: int | None = Field(default=None, ge=1)
    death_year: int | None = Field(default=None, ge=1)

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @model_validator(mode="after")
    def years_consistent(self):
        if self.birth_year and self.death_year and self.death_year < self.birth_year:
            raise ValueError("death_year must be >= birth_year")
        return self


class AuthorRead(AuthorIn):
    id: int
