from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Category as CategoryModel
from internal.schemas.category_schema import CategoryCreateUpdateSchema, CategorySchema


class CategoriesRepository:
    @staticmethod
    async def get_categories(
        async_session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[CategorySchema]:
        async with async_session() as session:
            statement = select(CategoryModel).filter(CategoryModel.user_id == user_id)
            result = await session.execute(statement)
            categories: list[CategorySchema] = [
                CategorySchema(
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
        new_category: CategoryCreateUpdateSchema,
        user_id: str,
    ) -> None:
        category = CategoryModel(
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
    ) -> CategorySchema:
        async with async_session() as session:
            statement = select(CategoryModel).filter(
                CategoryModel.category_id == category_id
            )
            result = await session.execute(statement)
            categoryDB: CategoryModel = result.scalars().one()
            category = CategorySchema(
                category_id=categoryDB.category_id,
                category_name=categoryDB.category_name,
                category_description=categoryDB.category_description,
                category_type=categoryDB.category_type,
                user_id=categoryDB.user_id,
            )
            return category

    @staticmethod
    async def update_category(
        async_session: async_sessionmaker[AsyncSession],
        category_id: str,
        data: CategoryCreateUpdateSchema,
    ) -> CategorySchema:
        async with async_session() as session:
            statement = (
                update(CategoryModel)
                .where(CategoryModel.category_id == category_id)
                .values(
                    category_name=data.category_name,
                    category_description=data.category_description,
                    category_type=data.category_type,
                )
                .returning(CategoryModel)
            )
            result = await session.execute(statement)
            await session.commit()
            categoryDB: CategoryModel = result.scalars().one()
            category = CategorySchema(
                category_id=categoryDB.category_id,
                category_name=categoryDB.category_name,
                category_description=categoryDB.category_description,
                category_type=categoryDB.category_type,
                user_id=categoryDB.user_id,
            )
            return category

    @staticmethod
    async def delete_category(
        async_session: async_sessionmaker[AsyncSession], category_id: str
    ) -> None:
        async with async_session() as session:
            statement = delete(CategoryModel).where(
                CategoryModel.category_id == category_id
            )
            await session.execute(statement)
            await session.commit()
