from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.auth.utils import hash_password
from internal.databases.models import User as UserModel
from internal.schemas.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema


class UsersRepository:
    async def add_user(
        self,
        async_session: async_sessionmaker[AsyncSession],
        new_user: UserCreateSchema,
    ) -> None:
        user = UserModel(
            user_id=new_user.user_id,
            username=new_user.username,
            hashed_password=hash_password(new_user.password),
        )
        async with async_session() as session:
            session.add(user)
            await session.commit()

    async def get_user(
        self, async_session: async_sessionmaker[AsyncSession], username: str
    ) -> UserSchema:
        async with async_session() as session:
            statement = select(UserModel).filter(UserModel.username == username)
            result = await session.execute(statement)
            userDB: UserModel = result.scalars().one()
            user = UserSchema(
                user_id=userDB.user_id,
                username=userDB.username,
                hashed_password=userDB.hashed_password,
            )
            return user

    async def update_user(
        self,
        async_session: async_sessionmaker[AsyncSession],
        user_id: str,
        data: UserUpdateSchema,
    ) -> None:
        async with async_session() as session:
            statement = (
                update(UserModel)
                .where(
                    UserModel.user_id == user_id,
                    UserModel.hashed_password == hash_password(data.old_password),
                )
                .values(
                    username=data.username,
                    hashed_password=hash_password(data.new_password),
                )
            )
            await session.execute(statement)
            await session.commit()
