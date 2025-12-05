from typing import Sequence

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData

from app.controllers import duplicate_error_handler, not_found_error_handler
from app.dtos.category import CategoryCreateDTO, CategoryReadDTO, CategoryUpdateDTO
from app.models import Category
from sqlalchemy.orm import Session
from app.repositories.category import CategoryRepository
from app.repositories.user import provide_user_repo  # reuse session provider pattern


async def provide_category_repo(db_session: Session) -> CategoryRepository:
    return CategoryRepository(session=db_session, auto_commit=True)


class CategoryController(Controller):
    path = "/categories"
    tags = ["categories"]
    return_dto = CategoryReadDTO
    dependencies = {"category_repo": Provide(provide_category_repo)}
    exception_handlers = {
        NotFoundError: not_found_error_handler,
        DuplicateKeyError: duplicate_error_handler,
    }

    @get("/")
    async def list_categories(self, category_repo: CategoryRepository) -> Sequence[Category]:
        return category_repo.list()

    @get("/{id:int}")
    async def get_category(self, id: int, category_repo: CategoryRepository) -> Category:
        return category_repo.get(id)

    @post("/", dto=CategoryCreateDTO)
    async def create_category(self, data: DTOData[Category], category_repo: CategoryRepository) -> Category:
        return category_repo.add(Category(**data.as_builtins()))

    @patch("/{id:int}", dto=CategoryUpdateDTO)
    async def update_category(self, id: int, data: DTOData[Category], category_repo: CategoryRepository) -> Category:
        category, _ = category_repo.get_and_update(match_fields="id", id=id, **data.as_builtins())
        return category

    @delete("/{id:int}")
    async def delete_category(self, id: int, category_repo: CategoryRepository) -> None:
        category_repo.delete(id)
