import json

from aiokafka import AIOKafkaProducer
from fastapi import HTTPException

from internal.config.config import settings


class Producer:
    def __init__(self):
        self.KAFKA_TOPIC = "report_tasks"
        self.producer = AIOKafkaProducer(
            bootstrap_servers=[settings.KAFKA_URL],
        )

    async def produce_kafka_message(self, message: dict[str, str | int]) -> None:
        try:
            await self.producer.send(
                self.KAFKA_TOPIC,
                json.dumps(message).encode("utf-8"),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
