from internal.categories.repository.categories import CategoriesRepository


db = CategoriesRepository()

class CategoryService:
    async def get_categories(self, session):
        categories = await db.get_categories(session)
        return categories

    async def add_category(self, session, new_category):
        await db.add_category(session, new_category)

    async def get_category(self, session, category_id):
        category = await db.get_category(session, category_id)
        return category

    async def update_category(self, session, category_id, data):
        await db.update_category(session, category_id, data)

    async def delete_category(self, session, category):
        await db.delete_category(session, category)