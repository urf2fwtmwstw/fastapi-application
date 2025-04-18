import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from internal.auth.repository.users import UsersRepository
from internal.databases.database import get_db
from internal.reports.repository.reports_repository import ReportsRepository
from internal.services.report_service import ReportService
from internal.services.transaction_service import TransactionService
from internal.services.user_service import UserService
from internal.transactions.repository.transactions import TransactionsRepository

resources = {}
jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=UTC)


@scheduler.scheduled_job("cron", day=1, hour=0, minute=0, second=0)
async def generate_reports(
    service=ReportService(
        ReportsRepository(),
        TransactionService(TransactionsRepository()),
        UserService(UsersRepository()),
    ),
):
    date = datetime.now(tz=UTC)
    async for db in get_db():
        asyncio.run(await service.async_report_generation(db, date.year, date.month))


# OS signals handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    resources["message"] = "Initialized"
    scheduler.start()
    yield
    print("Cleaning up resources...")
    resources.clear()
    scheduler.shutdown()


# entry point
app = FastAPI(lifespan=lifespan, docs_url="/docs")


# root endpoint
@app.get("/")
async def root():
    return {"message": resources.get("message", "Resource not initialized")}
