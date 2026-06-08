from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator

from app.schemas.author import AuthorIn, AuthorRead
from app.schemas.base import BaseInputModel, BasePydanticModel


class Genre(StrEnum):
    FICTION = "fiction"
    NONFICTION = "nonfiction"
    SCIENCE = "science"
    HISTORY = "history"
    FANTASY = "fantasy"
    POETRY = "poetry"


CURRENT_YEAR = datetime.now().year


class BookBase(BasePydanticModel):
    title: str = Field(min_length=1, max_length=500)
    genre: Genre
    year: int = Field(ge=1800, le=CURRENT_YEAR)

    @field_validator("title")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class BookCreate(BookBase):
    author: AuthorIn


class BookUpdate(BasePydanticModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    author: AuthorIn | None = None
    genre: Genre | None = None
    year: int | None = Field(default=None, ge=1800, le=CURRENT_YEAR)


class BookRead(BasePydanticModel):
    id: int
    title: str
    author: AuthorRead
    genre: str
    year: int


class BulkResult(BasePydanticModel):
    inserted: int


class BookFilter(BasePydanticModel):
    title: str | None = None
    author: str | None = None
    genre: Genre | None = None
    year_from: int | None = None
    year_to: int | None = None


class SortField(StrEnum):
    year = "year"
    title = "title"
    id = "id"


class BookListParams(BaseInputModel):
    title: str | None = None
    author: str | None = None
    genre: Genre | None = None
    year_from: int | None = Field(default=None, ge=1800)
    year_to: int | None = Field(default=None, le=CURRENT_YEAR)
    sort: SortField = SortField.id
    desc: bool = False
    after_id: int | None = Field(default=None)
    limit: int = Field(default=50, ge=1, le=200)
