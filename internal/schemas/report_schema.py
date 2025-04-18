from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict


class ReportCreateSchema(BaseModel):
    report_id: UUID4 = uuid4()
    report_year_month: str
    month_income: float
    month_expenses: float
    balance: float
    most_expensive_categories: str | None
    user_id: UUID4

    model_config = ConfigDict(from_attributes=True)
