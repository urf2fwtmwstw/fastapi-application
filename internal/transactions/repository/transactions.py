from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Transaction
from internal.schemas.transaction_schema import (
    TransactionCreateUpdateModel,
    TransactionModel,
)


class TransactionsRepository:
    @staticmethod
    async def get_transactions(
        async_session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[TransactionModel]:
        async with async_session() as session:
            statement = select(Transaction).filter(Transaction.user_id == user_id)
            result = await session.execute(statement)
            transactions: list[TransactionModel] = [
                TransactionModel(
                    transaction_id=transaction.transaction_id,
                    transaction_type=transaction.transaction_type,
                    transaction_value=transaction.transaction_value,
                    transaction_date=transaction.transaction_date,
                    transaction_created=transaction.transaction_created,
                    transaction_description=transaction.transaction_description,
                    user_id=transaction.user_id,
                    category_id=transaction.category_id,
                )
                for transaction in result.scalars()
            ]
            return transactions

    @staticmethod
    async def add_transaction(
        async_session: async_sessionmaker[AsyncSession],
        new_transaction: TransactionCreateUpdateModel,
        user_id: str,
    ) -> None:
        transaction = Transaction(
            transaction_id=uuid4(),
            transaction_type=new_transaction.transaction_type,
            transaction_value=new_transaction.transaction_value,
            transaction_date=new_transaction.transaction_date,
            transaction_description=new_transaction.transaction_description,
            user_id=user_id,
            category_id=new_transaction.category_id,
        )
        async with async_session() as session:
            session.add(transaction)
            await session.commit()

    @staticmethod
    async def get_transaction(
        async_session: async_sessionmaker[AsyncSession], transaction_id: str
    ) -> TransactionModel:
        async with async_session() as session:
            statement = select(Transaction).filter(
                Transaction.transaction_id == transaction_id
            )
            result = await session.execute(statement)
            transaction_model: Transaction = result.scalars().one()
            transaction_schema = TransactionModel(
                transaction_id=transaction_model.transaction_id,
                transaction_type=transaction_model.transaction_type,
                transaction_value=transaction_model.transaction_value,
                transaction_date=transaction_model.transaction_date,
                transaction_created=transaction_model.transaction_created,
                transaction_description=transaction_model.transaction_description,
                user_id=transaction_model.user_id,
                category_id=transaction_model.category_id,
            )
            return transaction_schema

    @staticmethod
    async def update_transaction(
        async_session: async_sessionmaker[AsyncSession],
        transaction_id: str,
        data: TransactionCreateUpdateModel,
    ) -> None:
        async with async_session() as session:
            statement = (
                update(Transaction)
                .where(Transaction.transaction_id == transaction_id)
                .values(
                    transaction_type=data.transaction_type,
                    transaction_value=data.transaction_value,
                    transaction_date=data.transaction_date,
                    transaction_description=data.transaction_description,
                    category_id=data.category_id,
                )
            )
            await session.execute(statement)
            await session.commit()

    @staticmethod
    async def delete_transaction(
        async_session: async_sessionmaker[AsyncSession], transaction_id: str
    ) -> None:
        async with async_session() as session:
            statement = delete(Transaction).where(
                Transaction.transaction_id == transaction_id
            )
            await session.execute(statement)
            await session.commit()
