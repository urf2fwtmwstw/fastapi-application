from pydantic import BaseModel

from internal.schemas.report_schema import REPORTID


class KafkaFillReportMessage(BaseModel):
    report_id: REPORTID
