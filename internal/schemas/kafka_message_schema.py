from pydantic import UUID4, BaseModel


class CreateReportMessage(BaseModel):
    report_id: UUID4
    user_id: UUID4
    report_year: int
    report_month: int
