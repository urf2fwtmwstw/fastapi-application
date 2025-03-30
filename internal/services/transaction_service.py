from internal.transactions.repository.transactions import \
    TransactionsRepository


class TransactionService:
    def __init__(self, repo: TransactionsRepository):
        self.repo = repo

    async def get_transactions(self, session, user_id):
        transactions = await self.repo.get_transactions(session, user_id)
        return transactions

    async def add_transaction(self, session, new_transaction):
        await self.repo.add_transaction(session, new_transaction)

    async def get_transaction(self, session, transaction_id):
        transaction = await self.repo.get_transaction(session, transaction_id)
        return transaction

    async def update_transaction(self, session, transaction_id, data):
        await self.repo.update_transaction(session, transaction_id, data)

    async def delete_transaction(self, session, transaction):
        await self.repo.delete_transaction(session, transaction)