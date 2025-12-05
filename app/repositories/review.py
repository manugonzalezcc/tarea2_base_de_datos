"""Repository for Review operations."""

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Review


class ReviewRepository(SQLAlchemySyncRepository[Review]):
    model_type = Review

    def count_user_book_reviews(self, user_id: int, book_id: int) -> int:
        session: Session = self.session
        return session.scalar(
            select(func.count(Review.id)).where(Review.user_id == user_id, Review.book_id == book_id)
        ) or 0


async def provide_review_repo(db_session: Session) -> ReviewRepository:
    return ReviewRepository(session=db_session, auto_commit=True)
