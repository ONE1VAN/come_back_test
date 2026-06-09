import pytest
from pydantic import ValidationError

from app.schemas.book import BookCreate

A = {"first_name": "Frank", "last_name": "Herbert"}


def test_blank_title_rejected():
    with pytest.raises(ValidationError):
        BookCreate(title="   ", author=A, genre="fiction", year=2000)


def test_year_in_future_rejected():
    with pytest.raises(ValidationError):
        BookCreate(title="T", author=A, genre="fiction", year=3000)


def test_year_before_1800_rejected():
    with pytest.raises(ValidationError):
        BookCreate(title="T", author=A, genre="fiction", year=1700)


def test_unknown_genre_rejected():
    with pytest.raises(ValidationError):
        BookCreate(title="T", author=A, genre="cooking", year=2000)
