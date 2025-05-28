import asyncio
import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.controllers.auth import get_auth_user_info
from internal.databases.database import get_db
from internal.reports.repository import ReportsRepository
from internal.schemas.kafka_message_schema import CreateReportMessage
from internal.schemas.report_schema import (
    ReportCreateSchema,
    ReportSchema,
)
from internal.schemas.user_schema import UserSchema
from internal.services.report_service import ReportService
from internal.services.transaction_service import TransactionService
from internal.transactions.repository import TransactionsRepository
from internal.transport.consumer import Consumer
from internal.transport.producer import Producer

resources = {}


@asynccontextmanager
async def lifespan(router: APIRouter):
    # Initialize repositories and services
    resources["report_repository"] = ReportsRepository()
    resources["transaction_repository"] = TransactionsRepository()
    resources["transaction_service"] = TransactionService(
        resources["transaction_repository"]
    )
    resources["report_service"] = ReportService(
        resources["report_repository"], resources["transaction_service"]
    )

    # Initialize Kafka producer and consumer
    resources["kafka_producer"] = Producer()
    await resources["kafka_producer"].producer.start()
    kafka_consumer = Consumer(resources["report_service"])
    await kafka_consumer.report_consumer.start()
    asyncio.create_task(kafka_consumer.consume_create_report_message())

    yield

    await resources["kafka_producer"].producer.stop()
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


def get_kafka_producer():
    kafka_producer = resources.get("kafka_producer", None)
    if kafka_producer is None:
        raise ModuleNotFoundError('"kafka_producer" was not initialized')
    return kafka_producer


@router.post("/create_report")
async def create_report(
    producer: Annotated[Producer, Depends(get_kafka_producer)],
    report_data: ReportCreateSchema,
    user: UserSchema = Depends(get_auth_user_info),
) -> dict[str, UUID]:
    report_id = uuid.uuid4()
    message = CreateReportMessage(
        user_id=user.user_id,
        report_id=report_id,
        report_year=report_data.report_year,
        report_month=report_data.report_month,
    )
    await producer.produce_create_report_message(message)
    return {"report_id": report_id}


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
