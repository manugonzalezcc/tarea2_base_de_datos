"""Data Transfer Objects for Book endpoints."""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Book


class BookReadDTO(SQLAlchemyDTO[Book]):
    """DTO for reading book data."""

    config = SQLAlchemyDTOConfig()


class BookCreateDTO(SQLAlchemyDTO[Book]):
    """DTO for creating books."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "loans", "categories", "reviews"},
    )


class BookUpdateDTO(SQLAlchemyDTO[Book]):
    """DTO for updating books with partial data."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "loans", "categories", "reviews"},
        partial=True,
    )
