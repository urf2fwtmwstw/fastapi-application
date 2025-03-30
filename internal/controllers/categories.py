import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.categories.repository.categories import CategoriesRepository
from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.databases.models import Category
from internal.schemas.category_schema import (CategoryCreateUpdateModel,
                                              CategoryModel)
from internal.schemas.user_schema import UserModel
from internal.services.category_service import CategoryService

resources = {}

@asynccontextmanager
async def lifespan(router: APIRouter):
    category_repository = CategoriesRepository()
    resources["category_service"] = CategoryService(category_repository)
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)

def get_category_service():
    category_service = resources.get("category_service", None)
    if category_service is None:
        raise ModuleNotFoundError('"category_service" was not initialized')
    return category_service


@router.get("", response_model=List[CategoryModel])
async def get_all_categories(
        service: Annotated[CategoryService, Depends(get_category_service)],
        db: Annotated[async_sessionmaker[AsyncSession],Depends(get_db)],
        user: UserModel = Depends(get_auth_user_info),
):
    categories = await service.get_categories(db, user.user_id)
    return categories

@router.post("", status_code=HTTPStatus.CREATED)
async def create_new_category(
        category_data:CategoryCreateUpdateModel,
        service: Annotated[CategoryService, Depends(get_category_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
        user: UserModel = Depends(get_auth_user_info),
):
    new_category = Category(
        category_id=uuid.uuid4(),
        category_name=category_data.category_name,
        category_description=category_data.category_description,
        category_type=category_data.category_type,
        user_id=user.user_id,
    )
    await service.add_category(db, new_category)

@router.get("/{category_id}")
async def show_category(
        category_id: str,
        service: Annotated[CategoryService, Depends(get_category_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
):
    category = await service.get_category(db, category_id)
    return category

@router.put("/{category_id}")
async def edit_category(
        category_id: str,
        data: CategoryCreateUpdateModel,
        service: Annotated[CategoryService, Depends(get_category_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
):
    await service.update_category(db, category_id, data={
        "category_name": data.category_name,
        "category_description": data.category_description,
        "category_type": data.category_type,
    })
    category = await service.get_category(db, category_id)
    return category

@router.delete("/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
        category_id: str,
        service: Annotated[CategoryService, Depends(get_category_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
):
    category = await service.get_category(db, category_id)
    await service.delete_category(db, category)