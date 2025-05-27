import json

from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException

from internal.config.config import settings
from internal.databases.database import get_db
from internal.schemas.report_schema import ReportCreateSchema
from internal.services.report_service import ReportService


class Consumer:
    def __init__(self, report_service: ReportService):
        self.KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_URL
        self.KAFKA_TOPIC = "report_tasks"
        self.KAFKA_GROUP_ID = "report_consumer_group"
        self.report_service = report_service
        self.report_consumer = AIOKafkaConsumer(
            self.KAFKA_TOPIC,
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.KAFKA_GROUP_ID,
            auto_offset_reset="earliest",
        )

    async def consume_create_report_message(self):
        try:
            async for msg in self.report_consumer:
                try:
                    message = json.loads(msg.value.decode("utf-8"))
                    async for db in get_db():
                        await self.report_service.create_report(
                            db,
                            report_data=ReportCreateSchema(
                                report_id=message["report_id"],
                                user_id=message["user_id"],
                                report_year=message["report_year"],
                                report_month=message["report_month"],
                            ),
                        )
                except Exception as e:
                    raise HTTPException(status_code=500, detail=e)
        finally:
            await self.report_consumer.stop()
