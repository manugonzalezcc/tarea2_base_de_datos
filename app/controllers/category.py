"""Controller for Category endpoints."""

from typing import Sequence

from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData

from app.controllers import duplicate_error_handler, not_found_error_handler
from app.dtos.category import CategoryCreateDTO, CategoryReadDTO, CategoryUpdateDTO
from app.models import Category
from app.repositories.category import CategoryRepository, provide_category_repo


class CategoryController(Controller):
    """Controller for category management operations."""

    path = "/categories"
    tags = ["categories"]
    return_dto = CategoryReadDTO
    dependencies = {"categories_repo": Provide(provide_category_repo)}
    exception_handlers = {
        NotFoundError: not_found_error_handler,
        DuplicateKeyError: duplicate_error_handler,
    }

    @get("/")
    async def list_categories(self, categories_repo: CategoryRepository) -> Sequence[Category]:
        """Get all categories."""

        return categories_repo.list()

    @get("/{id:int}")
    async def get_category(self, id: int, categories_repo: CategoryRepository) -> Category:
        """Get a category by ID."""

        return categories_repo.get(id)

    @post("/", dto=CategoryCreateDTO)
    async def create_category(
        self,
        data: DTOData[Category],
        categories_repo: CategoryRepository,
    ) -> Category:
        """Create a new category."""

        return categories_repo.add(data.create_instance())

    @patch("/{id:int}", dto=CategoryUpdateDTO)
    async def update_category(
        self,
        id: int,
        data: DTOData[Category],
        categories_repo: CategoryRepository,
    ) -> Category:
        """Update a category by ID."""

        category, _ = categories_repo.get_and_update(
            match_fields="id",
            id=id,
            **data.as_builtins(),
        )
        return category

    @delete("/{id:int}")
    async def delete_category(self, id: int, categories_repo: CategoryRepository) -> None:
        """Delete a category by ID."""

        categories_repo.delete(id)
