"""Data Transfer Objects for Review endpoints."""

from datetime import date

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from pydantic import BaseModel

from app.models import Review


class ReviewUserDTO(BaseModel):
    id: int
    username: str
    fullname: str


class ReviewBookDTO(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    pages: int
    published_year: int


class ReviewReadDTO(BaseModel):
    """Read model for reviews including user and book relations."""

    id: int
    rating: int
    comment: str
    review_date: date
    user_id: int
    book_id: int
    user: ReviewUserDTO
    book: ReviewBookDTO


class ReviewCreateDTO(SQLAlchemyDTO[Review]):
    """DTO for creating reviews."""

    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "created_at",
            "updated_at",
            "user",
            "book",
        }
    )


class ReviewUpdateDTO(SQLAlchemyDTO[Review]):
    """DTO for updating reviews with partial data."""

    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "created_at",
            "updated_at",
            "user",
            "book",
        },
        partial=True,
    )
