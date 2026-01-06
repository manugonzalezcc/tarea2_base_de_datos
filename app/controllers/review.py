"""Controller for Review endpoints."""

from typing import Sequence

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException

from app.controllers import not_found_error_handler
from app.dtos.review import ReviewBookDTO, ReviewCreateDTO, ReviewReadDTO, ReviewUpdateDTO, ReviewUserDTO
from app.models import Review
from app.repositories.review import ReviewRepository, provide_review_repo


class ReviewController(Controller):
    """Controller for review management operations."""

    path = "/reviews"
    tags = ["reviews"]
    dependencies = {"reviews_repo": Provide(provide_review_repo)}
    exception_handlers = {
        NotFoundError: not_found_error_handler,
    }

    def _to_read_dto(self, review: Review) -> ReviewReadDTO:
        return ReviewReadDTO(
            id=review.id,
            rating=review.rating,
            comment=review.comment,
            review_date=review.review_date,
            user_id=review.user_id,
            book_id=review.book_id,
            user=ReviewUserDTO(
                id=review.user.id,
                username=review.user.username,
                fullname=review.user.fullname,
            ),
            book=ReviewBookDTO(
                id=review.book.id,
                title=review.book.title,
                author=review.book.author,
                isbn=review.book.isbn,
                pages=review.book.pages,
                published_year=review.book.published_year,
            ),
        )

    @get("/")
    async def list_reviews(self, reviews_repo: ReviewRepository) -> Sequence[ReviewReadDTO]:
        """Get all reviews."""

        return [self._to_read_dto(review) for review in reviews_repo.list()]

    @get("/{id:int}")
    async def get_review(self, id: int, reviews_repo: ReviewRepository) -> ReviewReadDTO:
        """Get a review by ID."""

        return self._to_read_dto(reviews_repo.get(id))

    @post("/", dto=ReviewCreateDTO)
    async def create_review(
        self,
        data: DTOData[Review],
        reviews_repo: ReviewRepository,
    ) -> ReviewReadDTO:
        """Create a new review with validations."""

        payload = data.as_builtins()
        rating = payload.get("rating")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="rating debe estar entre 1 y 5")

        user_id = payload.get("user_id")
        book_id = payload.get("book_id")
        if not isinstance(user_id, int) or not isinstance(book_id, int):
            raise HTTPException(status_code=400, detail="user_id y book_id son requeridos")

        if reviews_repo.count_for_user_and_book(user_id=user_id, book_id=book_id) >= 3:
            raise HTTPException(
                status_code=400,
                detail="No se permiten más de 3 reseñas del mismo usuario para el mismo libro",
            )

        return self._to_read_dto(reviews_repo.add(data.create_instance()))

    @patch("/{id:int}", dto=ReviewUpdateDTO)
    async def update_review(
        self,
        id: int,
        data: DTOData[Review],
        reviews_repo: ReviewRepository,
    ) -> ReviewReadDTO:
        """Update a review by ID."""

        patch_data = data.as_builtins()
        if "rating" in patch_data:
            rating = patch_data["rating"]
            if rating is not None and (not isinstance(rating, int) or rating < 1 or rating > 5):
                raise HTTPException(status_code=400, detail="rating debe estar entre 1 y 5")

        review, _ = reviews_repo.get_and_update(match_fields="id", id=id, **patch_data)
        return self._to_read_dto(review)

    @delete("/{id:int}")
    async def delete_review(self, id: int, reviews_repo: ReviewRepository) -> None:
        """Delete a review by ID."""

        reviews_repo.delete(id)
