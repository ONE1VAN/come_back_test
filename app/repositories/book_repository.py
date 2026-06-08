from app.models.book import BookDB
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BookDB]):
    _model = BookDB
