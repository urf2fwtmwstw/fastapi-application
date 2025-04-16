from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Category
from internal.schemas.category_schema import CategoryCreateUpdateModel, CategoryModel


class CategoriesRepository:
    @staticmethod
    async def get_categories(
        async_session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[CategoryModel]:
        async with async_session() as session:
            statement = select(Category).filter(Category.user_id == user_id)
            result = await session.execute(statement)
            categories: list[CategoryModel] = [
                CategoryModel(
                    category_id=category.category_id,
                    category_name=category.category_name,
                    category_description=category.category_description,
                    category_type=category.category_type,
                    user_id=category.user_id,
                )
                for category in result.scalars()
            ]
            return categories

    @staticmethod
    async def add_category(
        async_session: async_sessionmaker[AsyncSession],
        new_category: CategoryCreateUpdateModel,
        user_id: str,
    ) -> None:
        category = Category(
            category_id=uuid4(),
            category_name=new_category.category_name,
            category_description=new_category.category_description,
            category_type=new_category.category_type,
            user_id=user_id,
        )
        async with async_session() as session:
            session.add(category)
            await session.commit()

    @staticmethod
    async def get_category(
        async_session: async_sessionmaker[AsyncSession], category_id: str
    ) -> CategoryModel:
        async with async_session() as session:
            statement = select(Category).filter(Category.category_id == category_id)
            result = await session.execute(statement)
            category_model: Category = result.scalars().one()
            category_schema = CategoryModel(
                category_id=category_model.category_id,
                category_name=category_model.category_name,
                category_description=category_model.category_description,
                category_type=category_model.category_type,
                user_id=category_model.user_id,
            )
            return category_schema

    @staticmethod
    async def update_category(
        async_session: async_sessionmaker[AsyncSession],
        category_id: str,
        data: CategoryCreateUpdateModel,
    ) -> CategoryModel:
        async with async_session() as session:
            statement = (
                update(Category)
                .where(Category.category_id == category_id)
                .values(
                    category_name=data.category_name,
                    category_description=data.category_description,
                    category_type=data.category_type,
                )
                .returning(Category)
            )
            result = await session.execute(statement)
            await session.commit()
            category_model: Category = result.scalars().one()
            category_schema = CategoryModel(
                category_id=category_model.category_id,
                category_name=category_model.category_name,
                category_description=category_model.category_description,
                category_type=category_model.category_type,
                user_id=category_model.user_id,
            )
            return category_schema

    @staticmethod
    async def delete_category(
        async_session: async_sessionmaker[AsyncSession], category_id: str
    ) -> None:
        async with async_session() as session:
            statement = delete(Category).where(Category.category_id == category_id)
            await session.execute(statement)
            await session.commit()
