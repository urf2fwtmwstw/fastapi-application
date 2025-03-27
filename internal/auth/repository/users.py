from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import User
from internal.schemas.user_schema import UserUpdateModel


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


    async def update_user(self, async_session: async_sessionmaker[AsyncSession], user_id: str, data: UserUpdateModel):
        async with async_session() as session:
            statement = select(User).filter(User.user_id == user_id and User.hashed_password == data["old_password"])

            result = await session.execute(statement)

            categories = result.scalars().one()

            categories.username = data["username"]
            categories.hashed_password = data["new_password"]

            await session.commit()