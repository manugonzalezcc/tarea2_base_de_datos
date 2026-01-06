"""Data Transfer Objects for Category endpoints."""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Category


class CategoryReadDTO(SQLAlchemyDTO[Category]):
    """DTO for reading category data."""

    config = SQLAlchemyDTOConfig(exclude={"created_at", "updated_at", "books"})


class CategoryCreateDTO(SQLAlchemyDTO[Category]):
    """DTO for creating categories."""

    config = SQLAlchemyDTOConfig(exclude={"id", "created_at", "updated_at", "books"})


class CategoryUpdateDTO(SQLAlchemyDTO[Category]):
    """DTO for updating categories with partial data."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "books"},
        partial=True,
    )
