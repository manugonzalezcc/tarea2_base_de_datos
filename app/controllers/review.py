"""Controller for Review endpoints."""

from typing import Sequence

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from litestar import Controller, get, post, delete, patch
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException

from app.controllers import duplicate_error_handler, not_found_error_handler
from app.dtos.review import ReviewCreateDTO, ReviewReadDTO, ReviewUpdateDTO
from app.models import Review
from app.repositories.review import ReviewRepository, provide_review_repo


class ReviewController(Controller):
    path = "/reviews"
    tags = ["reviews"]
    return_dto = ReviewReadDTO
    dependencies = {"review_repo": Provide(provide_review_repo)}
    exception_handlers = {NotFoundError: not_found_error_handler, DuplicateKeyError: duplicate_error_handler}

    @get("/")
    async def list_reviews(self, review_repo: ReviewRepository) -> Sequence[Review]:
        return review_repo.list()

    @get("/{id:int}")
    async def get_review(self, id: int, review_repo: ReviewRepository) -> Review:
        return review_repo.get(id)

    @post("/", dto=ReviewCreateDTO)
    async def create_review(self, data: DTOData[Review], review_repo: ReviewRepository) -> Review:
        builtins = data.as_builtins()
        # validar rating
        rating = builtins.get("rating")
        if rating is None or not (1 <= int(rating) <= 5):
            raise HTTPException(status_code=400, detail="rating debe estar entre 1 y 5")
        # límite de 3 por usuario y libro
        user_id = builtins.get("user_id")
        book_id = builtins.get("book_id")
        if user_id is None or book_id is None:
            raise HTTPException(status_code=400, detail="user_id y book_id son requeridos")
        count = review_repo.count_user_book_reviews(user_id=user_id, book_id=book_id)
        if count >= 3:
            raise HTTPException(status_code=400, detail="Máximo 3 reseñas por usuario para cada libro")
        return review_repo.add(Review(**builtins))

    @patch("/{id:int}", dto=ReviewUpdateDTO)
    async def update_review(self, id: int, data: DTOData[Review], review_repo: ReviewRepository) -> Review:
        review, _ = review_repo.get_and_update(match_fields="id", id=id, **data.as_builtins())
        return review

    @delete("/{id:int}")
    async def delete_review(self, id: int, review_repo: ReviewRepository) -> None:
        review_repo.delete(id)
