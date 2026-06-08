from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDB, TimestampMixin

if TYPE_CHECKING:
    from app.models.author import AuthorDB


class BookDB(BaseDB, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    year: Mapped[int] = mapped_column(nullable=False, index=True)

    author: Mapped[AuthorDB] = relationship(back_populates="books")

    __table_args__ = (
        CheckConstraint("year >= 1800", name="ck_books_year_min"),
        UniqueConstraint("title", "author_id", "year", name="uq_book_natural_key"),
        Index("ix_books_genre_year", "genre", "year"),
    )
