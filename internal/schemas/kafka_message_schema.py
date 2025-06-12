from pydantic import BaseModel


class CreateReportMessage(BaseModel):
    report_id: str
    user_id: str
    report_year: int
    report_month: int
