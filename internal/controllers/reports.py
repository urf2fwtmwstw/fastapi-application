import asyncio
import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated

from aiokafka.errors import BrokerNotAvailableError, KafkaError
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dependencies import (
    Consumer,
    CreateReportMessage,
    Producer,
    ReportCreateSchema,
    ReportSchema,
    ReportService,
    ReportsRepository,
    TransactionService,
    TransactionsRepository,
    UserSchema,
    get_auth_user_info,
    get_db,
)

resources = {}
producer: Producer


@asynccontextmanager
async def lifespan(router: APIRouter):
    global producer
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
    try:
        producer = Producer()
        await producer.report_producer.start()
        kafka_consumer = Consumer(resources["report_service"])
        await kafka_consumer.report_consumer.start()
        asyncio.create_task(kafka_consumer.consume_create_report_message())
    except KafkaError as e:
        raise BrokerNotAvailableError(e)

    yield

    await producer.report_producer.stop()
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
    user: UserSchema = Depends(get_auth_user_info),
) -> dict[str, str]:
    report_id = str(uuid.uuid4())
    message = CreateReportMessage(
        user_id=str(user.user_id),
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
