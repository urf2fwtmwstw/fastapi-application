from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.auth.utils import hash_password
from internal.databases.models import User
from internal.schemas.user_schema import UserCreateModel, UserModel, UserUpdateModel


class UsersRepository:
    async def add_user(
        self, async_session: async_sessionmaker[AsyncSession], new_user: UserCreateModel
    ) -> None:
        user_model = User(
            user_id=new_user.user_id,
            username=new_user.username,
            hashed_password=hash_password(new_user.password),
        )
        async with async_session() as session:
            session.add(user_model)
            await session.commit()

    async def get_user(
        self, async_session: async_sessionmaker[AsyncSession], username: str
    ) -> UserModel:
        async with async_session() as session:
            statement = select(User).filter(User.username == username)
            result = await session.execute(statement)
            user_model: User = result.scalars().one()
            user_schema = UserModel(
                user_id=user_model.user_id,
                username=user_model.username,
                hashed_password=user_model.hashed_password,
            )
            return user_schema

    async def update_user(
        self,
        async_session: async_sessionmaker[AsyncSession],
        user_id: str,
        data: UserUpdateModel,
    ) -> None:
        async with async_session() as session:
            statement = (
                update(User)
                .where(
                    User.user_id == user_id,
                    User.hashed_password == hash_password(data.old_password),
                )
                .values(
                    username=data.username,
                    hashed_password=hash_password(data.new_password),
                )
            )
            await session.execute(statement)
            await session.commit()
