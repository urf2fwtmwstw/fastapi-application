from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.categories.repository import CategoriesRepository
from internal.schemas.category_schema import CategoryCreateUpdateSchema, CategorySchema


class CategoryService:
    def __init__(self, repo: CategoriesRepository):
        self.repo = repo

    async def get_categories(
        self, session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[CategorySchema]:
        categories: list[CategorySchema] = await self.repo.get_categories(
            session, user_id
        )
        return categories

    async def add_category(
        self,
        session: async_sessionmaker[AsyncSession],
        new_category: CategoryCreateUpdateSchema,
        user_id: str,
    ) -> None:
        await self.repo.add_category(session, new_category, user_id)

    async def get_category(
        self, session: async_sessionmaker[AsyncSession], category_id: str
    ) -> CategorySchema:
        category: CategorySchema = await self.repo.get_category(session, category_id)
        return category

    async def update_category(
        self,
        session: async_sessionmaker[AsyncSession],
        category_id: str,
        data: CategoryCreateUpdateSchema,
    ) -> CategorySchema:
        return await self.repo.update_category(session, category_id, data)

    async def delete_category(
        self, session: async_sessionmaker[AsyncSession], category_id: str
    ) -> None:
        await self.repo.delete_category(session, category_id)
