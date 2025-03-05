from internal.logger import logger
from internal.config.config import config
from internal.databases.schemas import TransactionModel, TransactionCreateModel
from internal.databases.database import CRUD, engine
from internal.databases.models import Transaction
from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from contextlib import asynccontextmanager
from typing import List
from http import HTTPStatus
import uuid


# OS signals handling
resource = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    resource["msg"] = "Initialized"
    yield
    print("Cleaning up resources...")
    resource.clear()


# entry point
app = FastAPI(lifespan=lifespan, docs_url='/')

# root endpoint
@app.get("/")
async def root():
    logger.info('Root endpoint accessed', service="Spending Tracker")
    return {"message": resource.get("msg", "Resource not initialized")}


# transactions
session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
db = CRUD()



@app.get('/transactions', response_model=List[TransactionModel])
async def get_all_transactions():
    transactions = await db.get_all(session)
    return transactions

@app.post('/transactions', status_code=HTTPStatus.CREATED)
async def create_transaction(transaction_data:TransactionCreateModel):
    new_transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        name= transaction_data.name,
    )
    transactions = await db.add(session, new_transaction)
    return transactions

@app.get('/transactions/{transaction_id}')
async def get_transaction(transaction_id):
    transaction = await db.get(session, transaction_id)
    return transaction

@app.patch('/transactions/{transaction_id}')
async def update_transaction(transaction_id: str, data: TransactionCreateModel):
    transaction = await db.get(session, transaction_id)
    result = await db.update(session, transaction_id, data={
        'name': data.name,
    })
    return transaction

@app.delete('/transactions/{transaction_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_transaction(transaction_id):
    transaction = await db.get(session, transaction_id)

    result = await db.delete(session, transaction)

    return result


#logging requests
@app.middleware('http')
async def log_request_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info("Request completed",service="Spending Tracker")
    return response