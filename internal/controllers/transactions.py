import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.databases.models import Transaction
from internal.schemas.transaction_schema import (TransactionCreateUpdateModel,
                                                 TransactionModel)
from internal.schemas.user_schema import UserModel
from internal.services.transaction_service import TransactionService
from internal.transactions.repository.transactions import \
    TransactionsRepository

resources = {}

@asynccontextmanager
async def lifespan(router: APIRouter):
    transaction_repository = TransactionsRepository()
    resources["transaction_service"] = TransactionService(transaction_repository)
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)

def get_transaction_service():
    transaction_service = resources.get("transaction_service", None)
    if transaction_service is None:
        raise ModuleNotFoundError('"transaction_service" was not initialized')
    return transaction_service


@router.get("", response_model=List[TransactionModel])
async def get_all_transactions(
        service: Annotated[TransactionService, Depends(get_transaction_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
):
    transactions = await service.get_transactions(db)
    return transactions

@router.post("", status_code=HTTPStatus.CREATED)
async def create_transaction(
        transaction_data:TransactionCreateUpdateModel,
        service: Annotated[TransactionService, Depends(get_transaction_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
        user: UserModel = Depends(get_auth_user_info),
):
    new_transaction = Transaction(
        transaction_id=uuid.uuid4(),
        transaction_type=transaction_data.transaction_type,
        transaction_value=transaction_data.transaction_value,
        transaction_date=transaction_data.transaction_date,
        transaction_description=transaction_data.transaction_description,
        user_id=user.user_id,
        category_id=transaction_data.category_id,
    )
    await service.add_transaction(db, new_transaction)

@router.get("/{transaction_id}")
async def show_transaction(
        transaction_id,
service: Annotated[TransactionService, Depends(get_transaction_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]
):
    category = await service.get_transaction(db, transaction_id)
    return category

@router.put("/{transaction_id}")
async def edit_transaction(
        transaction_id: str,
        service: Annotated[TransactionService, Depends(get_transaction_service)],
        data: TransactionCreateUpdateModel, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]
):
    await service.update_transaction(db, transaction_id, data={
        "transaction_type": data.transaction_type,
        "transaction_value": data.transaction_value,
        "transaction_date": data.transaction_date,
        "transaction_description": data.transaction_description,
        "category_id": data.category_id,
    })
    transaction = await service.get_transaction(db, transaction_id)
    return transaction

@router.delete("/{transaction_id}", status_code=HTTPStatus.NO_CONTENT)
async def remove_transaction(
        transaction_id: str,
        service: Annotated[TransactionService, Depends(get_transaction_service)],
        db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]
):
    transaction = await service.get_transaction(db, transaction_id)
    await service.delete_transaction(db, transaction)