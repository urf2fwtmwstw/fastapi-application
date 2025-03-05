from internal.databases.models import Transaction
from internal.config.config import SQLALCHEMY_DATABASE_URL
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

engine = create_async_engine(
    url=SQLALCHEMY_DATABASE_URL,
    echo=True,
)

class CRUD:
    async def get_all(self, async_session:async_sessionmaker[AsyncSession]):
        async with async_session() as session:
            statement = select(Transaction).order_by(Transaction.transaction_id)

            result = await session.execute(statement)

            return result.scalars()

    async def add(self, async_session:async_sessionmaker[AsyncSession], transactions:Transaction):
        async with async_session() as session:
            session.add(transactions)
            await session.commit()

        return transactions

    async def get(self, async_session:async_sessionmaker[AsyncSession], transaction_id:str):
        async with async_session() as session:
            statement = select(Transaction).filter(Transaction.transaction_id == transaction_id)

            result = await session.execute(statement)

            return result.scalars().one()

    async def update(self, async_session:async_sessionmaker[AsyncSession], transaction_id, data):
        async with async_session() as session:
            statement = select(Transaction).filter(Transaction.transaction_id == transaction_id)

            result = await session.execute(statement)

            transactions = result.scalars().one()

            transactions.name = data['name']

            await session.commit()

            return transactions


    async def delete(self, async_session:async_sessionmaker[AsyncSession], transactions:Transaction):
        async with async_session() as session:
            await session.delete(transactions)
            await session.commit()

