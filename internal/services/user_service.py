from internal.auth.repository.users import UsersRepository


class UserService:
    def __init__(self, repo: UsersRepository):
        self.repo = repo

    async def add_user(self, session, new_user):
        await self.repo.add_user(session, new_user)

    async def get_user(self, session, username):
        user = await self.repo.get_user(session, username)
        return user

    async def update_user(self, session, user_id, data):
        await self.repo.update_user(session, user_id, data)