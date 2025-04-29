import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.reports.repository import ReportsRepository
from internal.schemas.report_schema import (
    ReportCreateSchema,
    ReportSchema,
)
from internal.schemas.user_schema import UserSchema
from internal.services.report_service import ReportService
from internal.services.transaction_service import TransactionService
from internal.transactions.repository import TransactionsRepository

resources = {}


@asynccontextmanager
async def lifespan(router: APIRouter):
    resources["report_repository"] = ReportsRepository()
    resources["transaction_repository"] = TransactionsRepository()
    resources["transaction_service"] = TransactionService(
        resources["transaction_repository"]
    )
    resources["report_service"] = ReportService(
        resources["report_repository"], resources["transaction_service"]
    )
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)


def get_transaction_service():
    transaction_service = resources.get("transaction_service", None)
    if transaction_service is None:
        raise ModuleNotFoundError('"transaction_service" was not initialized')
    return transaction_service


def get_report_service():
    report_service = resources.get("report_service", None)
    if report_service is None:
        raise ModuleNotFoundError('"report_service" was not initialized')
    return report_service


@router.post("/create_report")
async def create_report(
    report_data: ReportCreateSchema,
    background_tasks: BackgroundTasks,
    service: Annotated[ReportService, Depends(get_report_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    user: UserSchema = Depends(get_auth_user_info),
) -> dict:
    report_id = uuid.uuid4()
    background_tasks.add_task(
        service.create_report,
        db,
        user.user_id,
        report_id,
        report_data.report_year,
        report_data.report_month,
    )
    return {"report_id": str(report_id)}


@router.get("/get_report", response_model=ReportSchema)
async def get_report(
    report_id: str,
    service: Annotated[ReportService, Depends(get_report_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> ReportSchema:
    report: ReportSchema = await service.get_report(db, report_id)
    return report


@router.delete("/delete_report", status_code=HTTPStatus.NO_CONTENT)
async def delete_report(
    report_id: str,
    service: Annotated[ReportService, Depends(get_report_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> None:
    await service.delete_report(db, report_id)
