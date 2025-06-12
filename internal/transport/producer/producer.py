import json

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from fastapi import HTTPException

from internal.config.config import settings
from internal.schemas.kafka_message_schema import CreateReportMessage


class Producer:
    def __init__(self):
        self.report_producer = AIOKafkaProducer(
            bootstrap_servers=[settings.KAFKA_URL],
            value_serializer=lambda message: json.dumps(message).encode("utf-8"),
        )

    async def produce_create_report_message(self, message: CreateReportMessage) -> None:
        try:
            await self.report_producer.send(
                "report_tasks",
                message.model_dump(),
            )
        except KafkaError as e:
            raise HTTPException(status_code=500, detail=e)
