from datetime import datetime
from enum import Enum

from pydantic import UUID4, BaseModel, ConfigDict


class TransactionType(str, Enum):
    income = "income"
    expenses = "expenses"


class TransactionSchema(BaseModel):
    transaction_id: UUID4
    transaction_type: TransactionType
    transaction_value: float
    transaction_date: datetime
    transaction_created: datetime
    transaction_description: str | None
    user_id: UUID4
    category_id: UUID4

    model_config = ConfigDict(
        from_attributes=True,
    )


class TransactionCreateUpdateSchema(BaseModel):
    transaction_type: TransactionType
    transaction_value: float
    transaction_date: datetime
    transaction_description: str | None
    category_id: UUID4

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "transaction_type": "income",
                "transaction_value": "99.99",
                "transaction_date": "2032-04-23T10:20:30.400+02:30",
                "transaction_description": "description",
                "category_id": "2eaa06c3-f21e-497d-84bf-c5c41333dffe",
            }
        },
    )
