"""Repository for Book database operations."""

from __future__ import annotations

from typing import Sequence

from advanced_alchemy.repository import SQLAlchemySyncRepository
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models import Book, Review, book_categories


class BookRepository(SQLAlchemySyncRepository[Book]):
    """Repository for book database operations."""

    model_type = Book

    def get_available_books(self) -> Sequence[Book]:
        """Return books with stock > 0."""

        return self.list(Book.stock > 0)

    def find_by_category(self, category_id: int) -> Sequence[Book]:
        """Return books belonging to a category."""

        stmt = (
            sa.select(Book)
            .join(book_categories, book_categories.c.book_id == Book.id)
            .where(book_categories.c.category_id == category_id)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_most_reviewed_books(self, limit: int = 10) -> Sequence[Book]:
        """Return books ordered by review count (desc)."""

        stmt = (
            sa.select(Book)
            .outerjoin(Review, Review.book_id == Book.id)
            .group_by(Book.id)
            .order_by(sa.func.count(Review.id).desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def update_stock(self, book_id: int, quantity: int) -> Book:
        """Update book stock by a quantity (delta)."""

        book = self.get(book_id)
        new_stock = book.stock + quantity
        if new_stock < 0:
            raise ValueError("stock no puede quedar negativo")
        book.stock = new_stock
        return self.update(book)

    def search_by_author(self, author_name: str) -> Sequence[Book]:
        """Search books by partial author name (case-insensitive)."""

        return self.list(Book.author.ilike(f"%{author_name}%"))


async def provide_book_repo(db_session: Session) -> BookRepository:
    """Provide book repository instance with auto-commit."""
    return BookRepository(session=db_session, auto_commit=True)
