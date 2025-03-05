from pydantic import BaseModel, ConfigDict

class TransactionModel(BaseModel):
    transaction_id: str
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class TransactionCreateModel(BaseModel):
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example":{
                "name":"name"
            }
        }
    )