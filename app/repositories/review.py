"""Repository for Review database operations."""

from decimal import Decimal

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Review


class ReviewRepository(SQLAlchemySyncRepository[Review]):
    """Repository for review database operations."""

    model_type = Review

    def count_for_user_and_book(self, user_id: int, book_id: int) -> int:
        """Return number of reviews a user has created for a given book."""

        stmt = select(func.count()).select_from(Review).where(
            Review.user_id == user_id,
            Review.book_id == book_id,
        )
        count = self.session.scalar(stmt)
        return int(count or 0)


async def provide_review_repo(db_session: Session) -> ReviewRepository:
    """Provide review repository instance with auto-commit."""

    return ReviewRepository(session=db_session, auto_commit=True)
