"""Controller for Book endpoints."""

from dataclasses import dataclass
from datetime import datetime

from typing import Annotated, Sequence

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from advanced_alchemy.filters import LimitOffset
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from app.controllers import duplicate_error_handler, not_found_error_handler
from app.dtos.book import BookCreateDTO, BookReadDTO, BookUpdateDTO
from app.models import Book, BookStats
from app.repositories.book import BookRepository, provide_book_repo


class BookController(Controller):
    """Controller for book management operations."""

    path = "/books"
    tags = ["books"]
    return_dto = BookReadDTO
    dependencies = {"books_repo": Provide(provide_book_repo)}
    exception_handlers = {
        NotFoundError: not_found_error_handler,
        DuplicateKeyError: duplicate_error_handler,
    }

    @get("/")
    async def list_books(self, books_repo: BookRepository) -> Sequence[Book]:
        """Get all books."""
        return books_repo.list()

    @get("/{id:int}")
    async def get_book(self, id: int, books_repo: BookRepository) -> Book:
        """Get a book by ID."""
        return books_repo.get(id)

    @post("/", dto=BookCreateDTO)
    async def create_book(
        self,
        data: DTOData[Book],
        books_repo: BookRepository,
    ) -> Book:
        """Create a new book."""
        payload = data.as_builtins()

        current_year = datetime.now().year
        published_year = payload.get("published_year")
        if not isinstance(published_year, int) or not (1000 <= published_year <= current_year):
            raise HTTPException(
                detail=f"El año de publicación debe estar entre 1000 y {current_year}",
                status_code=400,
            )

        stock = payload.get("stock")
        if stock is not None and (not isinstance(stock, int) or stock <= 0):
            raise HTTPException(
                detail="stock debe ser un entero mayor a 0",
                status_code=400,
            )

        language = payload.get("language")
        if not isinstance(language, str) or not language.strip():
            raise HTTPException(
                detail="language es requerido (código ISO 639-1 de 2 letras)",
                status_code=400,
            )

        normalized_language = language.strip().lower()
        if normalized_language not in {"es", "en", "fr", "de", "it", "pt"}:
            raise HTTPException(
                detail="language debe ser uno de: es, en, fr, de, it, pt",
                status_code=400,
            )

        instance = data.create_instance()
        instance.language = normalized_language

        return books_repo.add(instance)

    @patch("/{id:int}", dto=BookUpdateDTO)
    async def update_book(
        self,
        id: int,
        data: DTOData[Book],
        books_repo: BookRepository,
    ) -> Book:
        """Update a book by ID."""

        patch_data = data.as_builtins()
        if "stock" in patch_data:
            stock = patch_data["stock"]
            if stock is not None and (not isinstance(stock, int) or stock < 0):
                raise HTTPException(
                    detail="stock no puede ser negativo",
                    status_code=400,
                )

        if "language" in patch_data:
            language = patch_data["language"]
            if language is not None:
                if not isinstance(language, str) or not language.strip():
                    raise HTTPException(
                        detail="language debe ser un string no vacío",
                        status_code=400,
                    )
                normalized_language = language.strip().lower()
                if normalized_language not in {"es", "en", "fr", "de", "it", "pt"}:
                    raise HTTPException(
                        detail="language debe ser uno de: es, en, fr, de, it, pt",
                        status_code=400,
                    )
                patch_data["language"] = normalized_language

        book, _ = books_repo.get_and_update(match_fields="id", id=id, **patch_data)

        return book

    @delete("/{id:int}")
    async def delete_book(self, id: int, books_repo: BookRepository) -> None:
        """Delete a book by ID."""
        books_repo.delete(id)

    @get("/search/")
    async def search_book_by_title(
        self,
        title: str,
        books_repo: BookRepository,
    ) -> Sequence[Book]:
        """Search books by title."""
        return books_repo.list(Book.title.ilike(f"%{title}%"))

    @get("/available")
    async def get_available_books(self, books_repo: BookRepository) -> Sequence[Book]:
        """Get books with stock > 0."""

        return books_repo.get_available_books()

    @get("/by-category/{category_id:int}")
    async def get_books_by_category(self, category_id: int, books_repo: BookRepository) -> Sequence[Book]:
        """Get books by category id."""

        return books_repo.find_by_category(category_id)

    @get("/most-reviewed")
    async def get_most_reviewed_books(
        self,
        limit: Annotated[int, Parameter(query="limit", default=10, ge=1, le=50)],
        books_repo: BookRepository,
    ) -> Sequence[Book]:
        """Get most reviewed books."""

        return books_repo.get_most_reviewed_books(limit=limit)

    @dataclass
    class StockUpdate:
        quantity: int

    @patch("/{id:int}/stock")
    async def update_book_stock(
        self,
        id: int,
        data: StockUpdate,
        books_repo: BookRepository,
    ) -> Book:
        """Update book stock by delta quantity."""

        try:
            return books_repo.update_stock(book_id=id, quantity=data.quantity)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @get("/search-by-author")
    async def search_books_by_author(self, author: str, books_repo: BookRepository) -> Sequence[Book]:
        """Search books by author name."""

        return books_repo.search_by_author(author_name=author)

    @get("/filter")
    async def filter_books_by_year(
        self,
        year_from: Annotated[int, Parameter(query="from")],
        to: int,
        books_repo: BookRepository,
    ) -> Sequence[Book]:
        """Filter books by published year."""
        return books_repo.list(Book.published_year.between(year_from, to))

    @get("/recent")
    async def get_recent_books(
        self,
        limit: Annotated[int, Parameter(query="limit", default=10, ge=1, le=50)],
        books_repo: BookRepository,
    ) -> Sequence[Book]:
        """Get most recent books."""
        return books_repo.list(
            LimitOffset(offset=0, limit=limit),
            order_by=Book.created_at.desc(),
        )

    @get("/stats")
    async def get_book_stats(
        self,
        books_repo: BookRepository,
    ) -> BookStats:
        """Get statistics about books."""
        total_books = books_repo.count()
        if total_books == 0:
            return BookStats(
                total_books=0,
                average_pages=0,
                oldest_publication_year=None,
                newest_publication_year=None,
            )

        books = books_repo.list()

        average_pages = sum(book.pages for book in books) / total_books
        oldest_year = min(book.published_year for book in books)
        newest_year = max(book.published_year for book in books)

        return BookStats(
            total_books=total_books,
            average_pages=average_pages,
            oldest_publication_year=oldest_year,
            newest_publication_year=newest_year,
        )
