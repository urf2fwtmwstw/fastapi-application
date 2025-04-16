from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.schemas.transaction_schema import (
    TransactionCreateUpdateModel,
    TransactionModel,
)
from internal.transactions.repository.transactions import TransactionsRepository


class TransactionService:
    def __init__(self, repo: TransactionsRepository):
        self.repo = repo

    async def get_transactions(
        self, session: async_sessionmaker[AsyncSession], user_id: str
    ) -> list[TransactionModel]:
        transactions: list[TransactionModel] = await self.repo.get_transactions(
            session, user_id
        )
        return transactions

    async def add_transaction(
        self,
        session: async_sessionmaker[AsyncSession],
        new_transaction: TransactionCreateUpdateModel,
        user_id: str,
    ) -> None:
        await self.repo.add_transaction(session, new_transaction, user_id)

    async def get_transaction(
        self, session: async_sessionmaker[AsyncSession], transaction_id: str
    ) -> TransactionModel:
        transaction: TransactionModel = await self.repo.get_transaction(
            session, transaction_id
        )
        return transaction

    async def update_transaction(
        self,
        session: async_sessionmaker[AsyncSession],
        transaction_id: str,
        data: TransactionCreateUpdateModel,
    ) -> TransactionModel:
        return await self.repo.update_transaction(session, transaction_id, data)

    async def delete_transaction(
        self, session: async_sessionmaker[AsyncSession], transaction_id: str
    ) -> None:
        await self.repo.delete_transaction(session, transaction_id)
