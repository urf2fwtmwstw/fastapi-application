from internal.categories.repository.categories import CategoriesRepository



class CategoryService:
    def __init__(self, repo: CategoriesRepository):
        self.repo = repo

    async def get_categories(self, session):
        categories = await self.repo.get_categories(session)
        return categories

    async def add_category(self, session, new_category):
        await self.repo.add_category(session, new_category)

    async def get_category(self, session, category_id):
        category = await self.repo.get_category(session, category_id)
        return category

    async def update_category(self, session, category_id, data):
        await self.repo.update_category(session, category_id, data)

    async def delete_category(self, session, category):
        await self.repo.delete_category(session, category)