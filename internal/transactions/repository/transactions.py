from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Transaction
from internal.schemas.transaction_schema import TransactionCreateUpdateModel


class TransactionsRepository:
    async def get_transactions(self, async_session: async_sessionmaker[AsyncSession]):
        async with async_session() as session:
            statement = select(Transaction)

            result = await session.execute(statement)

            return result.scalars()


    async def add_transaction(self, async_session: async_sessionmaker[AsyncSession], transactions: Transaction):
        async with async_session() as session:
            session.add(transactions)
            await session.commit()


    async def get_transaction(self, async_session: async_sessionmaker[AsyncSession], transaction_id: str):
        async with async_session() as session:
            statement = select(Transaction).filter(Transaction.transaction_id == transaction_id)

            result = await session.execute(statement)

            return result.scalars().one()


    async def update_transaction(self, async_session: async_sessionmaker[AsyncSession], transaction_id: str, data: TransactionCreateUpdateModel):
        async with async_session() as session:
            statement = select(Transaction).filter(Transaction.transaction_id == transaction_id)

            result = await session.execute(statement)

            transactions = result.scalars().one()

            transactions.transaction_type = data["transaction_type"]
            transactions.transaction_value = data["transaction_value"]
            transactions.transaction_date = data["transaction_date"]
            transactions.transaction_description = data["transaction_description"]
            transactions.category_id = data["category_id"]

            await session.commit()


    async def delete_transaction(self, async_session: async_sessionmaker[AsyncSession], transactions: Transaction):
        async with async_session() as session:
            await session.delete(transactions)
            await session.commit()