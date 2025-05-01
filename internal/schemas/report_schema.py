from datetime import datetime
from enum import Enum

from pydantic import UUID4, BaseModel, ConfigDict


class ReportStatus(str, Enum):
    created = "CREATED"
    generated = "GENERATED"
    failed = "FAILED"


class ReportSchema(BaseModel):
    report_id: UUID4
    report_created: datetime | None = None
    report_year_month: str
    month_income: float | None = None
    month_expenses: float | None = None
    balance: float | None = None
    most_expensive_categories: str | None = None
    user_id: UUID4
    status: ReportStatus

    model_config = ConfigDict(from_attributes=True)


class ReportCreateSchema(BaseModel):
    report_year: int
    report_month: int

    model_config = ConfigDict(from_attributes=True)
