from internal.services.schemas.category_schema import CategoryModel, CategoryCreateUpdateModel
from internal.databases.database import session
from internal.databases.models import Category
from internal.categories.repository.categories import get_all_categories, get_category, add_category, update_category, delete_category
from fastapi import APIRouter
from typing import List
from http import HTTPStatus
import uuid


router = APIRouter()

@router.get("", response_model=List[CategoryModel])
async def get_categories():
    categories = await get_all_categories(session)
    return categories

@router.post("", status_code=HTTPStatus.CREATED)
async def create_category(category_data:CategoryCreateUpdateModel):
    new_category = Category(
        category_id=uuid.uuid4(),
        category_name=category_data.category_name,
        category_description=category_data.category_description,
        category_type=category_data.category_type,
    )
    category = await add_category(session, new_category)
    return category

@router.get("/{category_id}")
async def show_category(category_id):
    category = await get_category(session, category_id)
    return category

@router.put("/{category_id}")
async def update_category(category_id: str, data: CategoryCreateUpdateModel):
    category = await get_category(session, category_id)
    await update_category(session, category_id, data={
        "category_name": data.category_name,
        "category_description": data.category_description,
        "category_type": data.category_type,
    })
    return category

@router.delete("/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(category_id):
    category = await get_category(session, category_id)

    result = await delete_category(session, category)

    return result