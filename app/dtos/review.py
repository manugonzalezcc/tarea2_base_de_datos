"""DTOs for Review endpoints."""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DTOData
from litestar.exceptions import HTTPException

from app.models import Review


class ReviewReadDTO(SQLAlchemyDTO[Review]):
    """DTO for reading review data."""

    config = SQLAlchemyDTOConfig()


class ReviewCreateDTO(SQLAlchemyDTO[Review]):
    """DTO for creating reviews."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "user", "book"},
    )

    @staticmethod
    def validate(data: DTOData[Review]):
        builtins = data.as_builtins()
        rating = builtins.get("rating")
        if rating is None or not (1 <= int(rating) <= 5):
            raise HTTPException(status_code=400, detail="rating debe estar entre 1 y 5")


class ReviewUpdateDTO(SQLAlchemyDTO[Review]):
    """DTO for updating reviews."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "user", "book"},
        partial=True,
    )
