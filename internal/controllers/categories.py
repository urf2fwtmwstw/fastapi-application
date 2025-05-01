from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.categories.repository import CategoriesRepository
from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.schemas.category_schema import CategoryCreateUpdateSchema, CategorySchema
from internal.schemas.user_schema import UserSchema
from internal.services.category_service import CategoryService

resources = {}


@asynccontextmanager
async def lifespan(router: APIRouter):
    resources["category_repository"] = CategoriesRepository()
    resources["category_service"] = CategoryService(resources["category_repository"])
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)


def get_category_service():
    category_service = resources.get("category_service", None)
    if category_service is None:
        raise ModuleNotFoundError('"category_service" was not initialized')
    return category_service


@router.get("", response_model=List[CategorySchema])
async def get_all_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    user: UserSchema = Depends(get_auth_user_info),
) -> list[CategorySchema]:
    categories: list[CategorySchema] = await service.get_categories(db, user.user_id)
    return categories


@router.post("", status_code=HTTPStatus.CREATED)
async def create_new_category(
    category_data: CategoryCreateUpdateSchema,
    service: Annotated[CategoryService, Depends(get_category_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    user: UserSchema = Depends(get_auth_user_info),
) -> None:
    await service.add_category(db, category_data, user.user_id)


@router.get("/{category_id}")
async def get_category(
    category_id: str,
    service: Annotated[CategoryService, Depends(get_category_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> CategorySchema:
    category: CategorySchema = await service.get_category(db, category_id)
    return category


@router.put("/{category_id}")
async def edit_category(
    category_id: str,
    data: CategoryCreateUpdateSchema,
    service: Annotated[CategoryService, Depends(get_category_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> CategorySchema:
    category: CategorySchema = await service.update_category(db, category_id, data)
    return category


@router.delete("/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    category_id: str,
    service: Annotated[CategoryService, Depends(get_category_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> None:
    await service.delete_category(db, category_id)
