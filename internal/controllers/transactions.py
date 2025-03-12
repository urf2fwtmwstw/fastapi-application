from internal.transactions.repository.transactions import Repository
from internal.services.schemas.transaction_schema import TransactionModel, TransactionCreateUpdateModel
from internal.databases.database import session
from internal.databases.models import Transaction
from fastapi import APIRouter
from typing import List
from http import HTTPStatus
import uuid


router = APIRouter()

@router.get("", response_model=List[TransactionModel])
async def get_transactions():
    transactions = await Repository().get_all_transactions(session)
    return transactions

@router.post("", status_code=HTTPStatus.CREATED)
async def create_transaction(transaction_data:TransactionCreateUpdateModel):
    new_transaction = Transaction(
        transaction_id=uuid.uuid4(),
        transaction_type=transaction_data.transaction_type,
        transaction_value=transaction_data.transaction_value,
        transaction_date=transaction_data.transaction_date,
        transaction_description=transaction_data.transaction_description,
        category_id=transaction_data.category_id,
    )
    transaction = await Repository().add_transaction(session, new_transaction)
    return transaction

@router.get("/{transaction_id}")
async def show_transaction(transaction_id):
    category = await Repository().get_transaction(session, transaction_id)
    return category

@router.put("/{transaction_id}")
async def upd_transaction(transaction_id: str, data: TransactionCreateUpdateModel):
    transaction = await Repository().get_transaction(session, transaction_id)
    await Repository().update_transaction(session, transaction_id, data={
        "transaction_type": data.transaction_type,
        "transaction_value": data.transaction_value,
        "transaction_date": data.transaction_date,
        "transaction_description": data.transaction_description,
        "category_id": data.category_id,
    })
    return transaction

@router.delete("/{transaction_id}", status_code=HTTPStatus.NO_CONTENT)
async def remove_transaction(transaction_id):
    transaction = await Repository().get_transaction(session, transaction_id)

    result = await Repository().delete_transaction(session, transaction)

    return result