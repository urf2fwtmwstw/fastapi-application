import json

from aiokafka import AIOKafkaConsumer

from internal.config.config import settings
from internal.databases.database import get_db
from internal.services.report_service import ReportService


class Consumer:
    def __init__(self, report_service: ReportService):
        self.KAFKA_BOOTSTRAP_SERVERS = settings.KAFKA_URL
        self.KAFKA_TOPIC = "report_tasks"
        self.KAFKA_GROUP_ID = "report_consumer_group"
        self.report_service = report_service
        self.consumer = AIOKafkaConsumer(
            self.KAFKA_TOPIC,
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id=self.KAFKA_GROUP_ID,
            auto_offset_reset="earliest",
        )

    async def consume(self):
        try:
            async for msg in self.consumer:
                try:
                    message = json.loads(msg.value.decode("utf-8"))
                    user_id: str = message["user_id"]
                    report_id: str = message["report_id"]
                    report_year: int = message["report_year"]
                    report_month: int = message["report_month"]
                    async for db in get_db():
                        await self.report_service.create_report(
                            db,
                            user_id,
                            report_id,
                            report_year,
                            report_month,
                        )
                except Exception as e:
                    raise e
        finally:
            await self.consumer.stop()
