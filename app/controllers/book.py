"""Controller for Book endpoints."""

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
from app.models import Category


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
        # Validar que el año esté entre 1000 y el año actual
        if not (1000 <= data.as_builtins()["published_year"] <= 2024):
            raise HTTPException(
                detail="El año de publicación debe estar entre 1000 y 2024",
                status_code=400,
            )
        return books_repo.add(data.create_instance())

    @patch("/{id:int}", dto=BookUpdateDTO)
    async def update_book(
        self,
        id: int,
        data: DTOData[Book],
        books_repo: BookRepository,
    ) -> Book:
        """Update a book by ID.
        Maneja explícitamente la relación many-to-many `categories` para evitar errores de duplicado.
        """
        # Cargar libro existente
        book = books_repo.get(id)

        payload = data.as_builtins()

        # Actualizar campos simples si están presentes en el payload
        for field in ("title", "author", "isbn", "pages", "published_year"):
            if field in payload and payload[field] is not None:
                setattr(book, field, payload[field])

        # Actualizar relación de categorías si viene en el payload
        if "categories" in payload and payload["categories"] is not None:
            categories_payload = payload["categories"]
            # Convertir a instancias de Category basadas en id
            session = books_repo.session  # usar la sesión del repositorio
            new_categories: list[Category] = []
            for c in categories_payload:
                # c puede ser dict o instancia Category
                if isinstance(c, dict):
                    cid = c.get("id")
                    name = c.get("name")
                else:
                    cid = getattr(c, "id", None)
                    name = getattr(c, "name", None)

                if cid is not None:
                    existing = session.get(Category, cid)
                    if existing:
                        new_categories.append(existing)
                        continue
                if name is not None:
                    existing = session.query(Category).filter(Category.name == name).first()
                    if existing:
                        new_categories.append(existing)
                    else:
                        new_categories.append(Category(name=name))
            book.categories = new_categories

        # Commit de los cambios usando el repositorio
        session = books_repo.session
        session.add(book)
        session.commit()
        session.refresh(book)
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
