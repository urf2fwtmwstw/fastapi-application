from internal.databases.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class UsersRepository:
    async def add_user(self, async_session: async_sessionmaker[AsyncSession], users: User):
        async with async_session() as session:
            session.add(users)
            await session.commit()


    async def get_user(self, async_session: async_sessionmaker[AsyncSession], username: str):
        async with async_session() as session:
            statement = select(User).filter(User.username == username)

            result = await session.execute(statement)

            return result.scalars().one()


    async def update_user(self, async_session: async_sessionmaker[AsyncSession], user_id: str, data):
        async with async_session() as session:
            statement = select(User).filter(User.user_id == user_id)

            result = await session.execute(statement)

            categories = result.scalars().one()

            categories.username = data["username"]
            categories.hashed_password = data["hashed_password"]

            await session.commit()


    async def delete_user(self, async_session: async_sessionmaker[AsyncSession], users: User):
        async with async_session() as session:
            await session.delete(users)
            await session.commit()