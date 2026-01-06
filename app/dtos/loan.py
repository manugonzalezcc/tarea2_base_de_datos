"""Data Transfer Objects for Loan endpoints."""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Loan


class LoanReadDTO(SQLAlchemyDTO[Loan]):
    """DTO for reading loan data."""

    config = SQLAlchemyDTOConfig(
        exclude={"user", "book"},
    )


class LoanCreateDTO(SQLAlchemyDTO[Loan]):
    """DTO for creating loans."""

    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at", "user", "book", "due_date", "fine_amount", "status"},
    )


class LoanUpdateDTO(SQLAlchemyDTO[Loan]):
    """DTO for updating loans with partial data."""

    config = SQLAlchemyDTOConfig(include={"status"}, partial=True)
