from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Category
from internal.schemas.category_schema import CategoryCreateUpdateModel


class CategoriesRepository:
    async def get_categories(self, async_session: async_sessionmaker[AsyncSession], user_id: str):
        async with async_session() as session:
            statement = select(Category).filter(Category.user_id == user_id)

            result = await session.execute(statement)

            return result.scalars()


    async def add_category(self, async_session: async_sessionmaker[AsyncSession], categories: Category):
        async with async_session() as session:
            session.add(categories)
            await session.commit()


    async def get_category(self, async_session: async_sessionmaker[AsyncSession], category_id: str):
        async with async_session() as session:
            statement = select(Category).filter(Category.category_id == category_id)

            result = await session.execute(statement)

            return result.scalars().one()


    async def update_category(self, async_session: async_sessionmaker[AsyncSession], category_id: str, data: CategoryCreateUpdateModel):
        async with async_session() as session:
            statement = select(Category).filter(Category.category_id == category_id)

            result = await session.execute(statement)

            categories = result.scalars().one()

            categories.category_name = data["category_name"]
            categories.category_description = data["category_description"]
            categories.category_type = data["category_type"]

            await session.commit()


    async def delete_category(self, async_session: async_sessionmaker[AsyncSession], categories: Category):
        async with async_session() as session:
            await session.delete(categories)
            await session.commit()