import json

from aiokafka import AIOKafkaProducer
from fastapi import HTTPException

from internal.config.config import settings
from internal.schemas.kafka_message_schema import CreateReportMessage


class Producer:
    def __init__(self):
        self.KAFKA_TOPIC = "report_tasks"
        self.producer = AIOKafkaProducer(
            bootstrap_servers=[settings.KAFKA_URL],
        )

    async def produce_create_report_message(self, message: CreateReportMessage) -> None:
        try:
            message: dict[str, str | int] = {
                "report_id": str(message.report_id),
                "user_id": str(message.user_id),
                "report_year": message.report_year,
                "report_month": message.report_month,
            }
            await self.producer.send(
                self.KAFKA_TOPIC,
                json.dumps(message).encode("utf-8"),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
