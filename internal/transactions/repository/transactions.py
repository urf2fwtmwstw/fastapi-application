from uuid import uuid4

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Transaction as TransactionModel
from internal.schemas.transaction_schema import (
    TransactionCreateUpdateSchema,
    TransactionSchema,
)


class TransactionsRepository:
    @staticmethod
    async def get_transactions(
        async_session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[TransactionSchema]:
        async with async_session() as session:
            statement = (
                select(TransactionModel)
                .filter(TransactionModel.user_id == user_id)
                .order_by(desc(TransactionModel.transaction_date))
            )
            result = await session.execute(statement)
            transactions: list[TransactionSchema] = [
                TransactionSchema(
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
        new_transaction: TransactionCreateUpdateSchema,
        user_id: str,
    ) -> None:
        transaction = TransactionModel(
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
    ) -> TransactionSchema:
        async with async_session() as session:
            statement = select(TransactionModel).filter(
                TransactionModel.transaction_id == transaction_id
            )
            result = await session.execute(statement)
            transactionDB: TransactionModel = result.scalars().one()
            transaction = TransactionSchema(
                transaction_id=transactionDB.transaction_id,
                transaction_type=transactionDB.transaction_type,
                transaction_value=transactionDB.transaction_value,
                transaction_date=transactionDB.transaction_date,
                transaction_created=transactionDB.transaction_created,
                transaction_description=transactionDB.transaction_description,
                user_id=transactionDB.user_id,
                category_id=transactionDB.category_id,
            )
            return transaction

    @staticmethod
    async def update_transaction(
        async_session: async_sessionmaker[AsyncSession],
        transaction_id: str,
        data: TransactionCreateUpdateSchema,
    ) -> TransactionSchema:
        async with async_session() as session:
            statement = (
                update(TransactionModel)
                .where(TransactionModel.transaction_id == transaction_id)
                .values(
                    transaction_type=data.transaction_type,
                    transaction_value=data.transaction_value,
                    transaction_date=data.transaction_date,
                    transaction_description=data.transaction_description,
                    category_id=data.category_id,
                )
                .returning(TransactionModel)
            )
            result = await session.execute(statement)
            await session.commit()
            transactionDB: TransactionModel = result.scalars().one()
            transaction = TransactionSchema(
                transaction_id=transactionDB.transaction_id,
                transaction_type=transactionDB.transaction_type,
                transaction_value=transactionDB.transaction_value,
                transaction_date=transactionDB.transaction_date,
                transaction_created=transactionDB.transaction_created,
                transaction_description=transactionDB.transaction_description,
                user_id=transactionDB.user_id,
                category_id=transactionDB.category_id,
            )
            return transaction

    @staticmethod
    async def delete_transaction(
        async_session: async_sessionmaker[AsyncSession], transaction_id: str
    ) -> None:
        async with async_session() as session:
            statement = delete(TransactionModel).where(
                TransactionModel.transaction_id == transaction_id
            )
            await session.execute(statement)
            await session.commit()
