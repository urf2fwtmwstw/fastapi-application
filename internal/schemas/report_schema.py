from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportStatus(str, Enum):
    created = "CREATED"
    generated = "GENERATED"
    failed = "FAILED"


class ReportSchema(BaseModel):
    report_id: UUID
    report_created: datetime | None = None
    report_year_month: str
    month_income: float | None = None
    month_expenses: float | None = None
    balance: float | None = None
    most_expensive_categories: str | None = None
    user_id: UUID
    status: ReportStatus

    model_config = ConfigDict(from_attributes=True)


class ReportCreateSchema(BaseModel):
    report_id: UUID | None = None
    user_id: str | None = None
    report_year: int
    report_month: int
