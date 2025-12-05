from advanced_alchemy.repository import SQLAlchemySyncRepository

from app.models import Category


class CategoryRepository(SQLAlchemySyncRepository[Category]):
    model_type = Category
