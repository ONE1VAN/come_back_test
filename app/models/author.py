from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDB, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import BookDB


class AuthorDB(BaseDB, TimestampMixin):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_year: Mapped[int | None] = mapped_column(nullable=True)
    death_year: Mapped[int | None] = mapped_column(nullable=True)

    books: Mapped[list[BookDB]] = relationship(back_populates="author")

    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "birth_year",
            name="uq_author_identity",
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_authors_name", "last_name", "first_name"),
        Index("ix_authors_birth_year", "birth_year"),
        CheckConstraint(
            "death_year IS NULL OR birth_year IS NULL OR death_year >= birth_year",
            name="ck_author_years",
        ),
    )
