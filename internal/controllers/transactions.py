from internal.services.transaction_service import TransactionsService
from internal.schemas.transaction_schema import TransactionModel, TransactionCreateUpdateModel
from internal.databases.database import get_db
from internal.databases.models import Transaction
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import APIRouter, Depends
from typing import List, Annotated
from http import HTTPStatus
import uuid


router = APIRouter()
transactions_repo = TransactionsService()

@router.get("", response_model=List[TransactionModel])
async def get_all_transactions(db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    transactions = await transactions_repo.get_transactions(db)
    return transactions

@router.post("", status_code=HTTPStatus.CREATED)
async def create_transaction(transaction_data:TransactionCreateUpdateModel, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    new_transaction = Transaction(
        transaction_id=uuid.uuid4(),
        transaction_type=transaction_data.transaction_type,
        transaction_value=transaction_data.transaction_value,
        transaction_date=transaction_data.transaction_date,
        transaction_description=transaction_data.transaction_description,
        category_id=transaction_data.category_id,
    )
    await transactions_repo.add_transaction(db, new_transaction)

@router.get("/{transaction_id}")
async def show_transaction(transaction_id, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    category = await transactions_repo.get_transaction(db, transaction_id)
    return category

@router.put("/{transaction_id}")
async def upd_transaction(transaction_id: str, data: TransactionCreateUpdateModel, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    await transactions_repo.update_transaction(db, transaction_id, data={
        "transaction_type": data.transaction_type,
        "transaction_value": data.transaction_value,
        "transaction_date": data.transaction_date,
        "transaction_description": data.transaction_description,
        "category_id": data.category_id,
    })
    transaction = await transactions_repo.get_transaction(db, transaction_id)
    return transaction

@router.delete("/{transaction_id}", status_code=HTTPStatus.NO_CONTENT)
async def remove_transaction(transaction_id, db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)]):
    transaction = await transactions_repo.get_transaction(db, transaction_id)
    await transactions_repo.delete_transaction(db, transaction)