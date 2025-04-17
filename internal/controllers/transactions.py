from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.schemas.transaction_schema import (
    TransactionCreateUpdateSchema,
    TransactionSchema,
)
from internal.schemas.user_schema import UserSchema
from internal.services.transaction_service import TransactionService
from internal.transactions.repository.transactions import TransactionsRepository

resources = {}


@asynccontextmanager
async def lifespan(router: APIRouter):
    resources["transaction_repository"] = TransactionsRepository()
    resources["transaction_service"] = TransactionService(
        resources["transaction_repository"]
    )
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)


def get_transaction_service():
    transaction_service = resources.get("transaction_service", None)
    if transaction_service is None:
        raise ModuleNotFoundError('"transaction_service" was not initialized')
    return transaction_service


@router.get("", response_model=List[TransactionSchema])
async def get_all_transactions(
    service: Annotated[TransactionService, Depends(get_transaction_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    user: UserSchema = Depends(get_auth_user_info),
) -> list[TransactionSchema]:
    transactions: list[TransactionSchema] = await service.get_transactions(
        db, user.user_id
    )
    return transactions


@router.post("", status_code=HTTPStatus.CREATED)
async def create_transaction(
    transaction_data: TransactionCreateUpdateSchema,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    user: UserSchema = Depends(get_auth_user_info),
) -> None:
    await service.add_transaction(db, transaction_data, user.user_id)


@router.get("/{transaction_id}")
async def show_transaction(
    transaction_id,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TransactionSchema:
    transaction: TransactionSchema = await service.get_transaction(db, transaction_id)
    return transaction


@router.put("/{transaction_id}")
async def edit_transaction(
    transaction_id: str,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
    data: TransactionCreateUpdateSchema,
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TransactionSchema:
    transaction: TransactionSchema = await service.update_transaction(
        db, transaction_id, data
    )
    return transaction


@router.delete("/{transaction_id}", status_code=HTTPStatus.NO_CONTENT)
async def remove_transaction(
    transaction_id: str,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> None:
    await service.delete_transaction(db, transaction_id)
