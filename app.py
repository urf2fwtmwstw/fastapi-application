from asyncio import run
from contextlib import asynccontextmanager

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from internal.databases.database import get_db
from internal.reports.repository.reports_repository import ReportsRepository
from internal.services.report_service import ReportService
from internal.services.transaction_service import TransactionService
from internal.transactions.repository.transactions import TransactionsRepository

resources = {}
jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Moscow")
trigger = CronTrigger(year="*", month="*", day="18", hour="3", minute="16", second="0")


@scheduler.scheduled_job("cron", day=1, hour=0, minute=0, second=0)
async def generate_reports(
    service=ReportService(
        ReportsRepository(), TransactionService(TransactionsRepository())
    ),
):
    async for db in get_db():
        await service.add_report(db, "5f5a0067-e1f4-43ec-854d-c571850b61fd", 2025, 4)


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
