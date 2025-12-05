from litestar.dto import DTOConfig
from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO

from app.models import Category


class CategoryReadDTO(SQLAlchemyDTO[Category]):
    config = DTOConfig(
        include={"id", "name", "description"},
        max_nested_depth=0,
    )


class CategoryCreateDTO(SQLAlchemyDTO[Category]):
    config = DTOConfig(
        include={"name", "description"},
    )


class CategoryUpdateDTO(SQLAlchemyDTO[Category]):
    config = DTOConfig(
        include={"name", "description"},
    )
