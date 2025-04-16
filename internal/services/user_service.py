from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.auth.repository.users import UsersRepository
from internal.schemas.user_schema import UserCreateModel, UserModel, UserUpdateModel


class UserService:
    def __init__(self, repo: UsersRepository):
        self.repo = repo

    async def add_user(
        self, session: async_sessionmaker[AsyncSession], new_user: UserCreateModel
    ) -> None:
        return await self.repo.add_user(session, new_user)

    async def get_user(
        self, session: async_sessionmaker[AsyncSession], username: str
    ) -> UserModel:
        user = await self.repo.get_user(session, username)
        return user

    async def update_user(
        self,
        session: async_sessionmaker[AsyncSession],
        user_id: str,
        data: UserUpdateModel,
    ) -> None:
        await self.repo.update_user(session, user_id, data)
