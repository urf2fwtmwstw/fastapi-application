from internal.transactions.repository.transactions import TransactionsRepository


db = TransactionsRepository()

class TransactionsService:
    async def get_transactions(self, session):
        transactions = await db.get_transactions(session)
        return transactions

    async def add_transaction(self, session, new_transaction):
        await db.add_transaction(session, new_transaction)

    async def get_transaction(self, session, transaction_id):
        transaction = await db.get_transaction(session, transaction_id)
        return transaction

    async def update_transaction(self, session, transaction_id, data):
        await db.update_transaction(session, transaction_id, data)

    async def delete_transaction(self, session, transaction):
        await db.delete_transaction(session, transaction)