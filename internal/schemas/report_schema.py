from pydantic import UUID4, BaseModel, ConfigDict


class ReportSchema(BaseModel):
    report_id: UUID4
    report_year_month: str
    month_income: float
    month_expenses: float
    balance: float
    most_expensive_categories: str | None
    user_id: UUID4

    model_config = ConfigDict(from_attributes=True)


class ReportCreateSchema(BaseModel):
    report_year: int
    report_month: int

    model_config = ConfigDict(from_attributes=True)
