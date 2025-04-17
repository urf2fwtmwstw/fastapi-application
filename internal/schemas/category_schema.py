from enum import Enum

from pydantic import UUID4, BaseModel, ConfigDict


class CategoryType(str, Enum):
    income = "income"
    expenses = "expenses"


class CategorySchema(BaseModel):
    category_id: UUID4
    category_name: str
    category_description: str | None
    category_type: CategoryType
    user_id: UUID4

    model_config = ConfigDict(
        from_attributes=True,
    )


class CategoryCreateUpdateSchema(BaseModel):
    category_name: str
    category_description: str | None
    category_type: CategoryType

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "category_name": "category name",
                "category_description": "description",
                "category_type": "income",
            }
        },
    )
