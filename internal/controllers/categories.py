from internal.schemas.category_schema import CategoryModel, CategoryCreateUpdateModel
from internal.services.category_service import CategoryService
from internal.databases.models import Category
from internal.databases.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, Depends
from typing import List, Annotated
from http import HTTPStatus
import uuid


router = APIRouter()
categories_repo = CategoryService()

@router.get("", response_model=List[CategoryModel])
async def get_all_categories(db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    categories = await categories_repo.get_categories(db)
    return categories

@router.post("", status_code=HTTPStatus.CREATED)
async def create_new_category(
        category_data:CategoryCreateUpdateModel,
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
):
    new_category = Category(
        category_id=uuid.uuid4(),
        category_name=category_data.category_name,
        category_description=category_data.category_description,
        category_type=category_data.category_type,
    )
    await categories_repo.add_category(db, new_category)

@router.get("/{category_id}")
async def show_category(category_id, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    category = await categories_repo.get_category(db, category_id)
    return category

@router.put("/{category_id}")
async def edit_category(category_id: str, data: CategoryCreateUpdateModel, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    await categories_repo.update_category(db, category_id, data={
        "category_name": data.category_name,
        "category_description": data.category_description,
        "category_type": data.category_type,
    })
    category = await categories_repo.get_category(db, category_id)
    return category

@router.delete("/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(category_id, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    category = await categories_repo.get_category(db, category_id)
    await categories_repo.delete_category(db, category)