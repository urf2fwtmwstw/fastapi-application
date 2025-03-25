from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict, UUID4


class UserModel(BaseModel):
    model_config = ConfigDict(strict=True)

    user_id: UUID4
    username: str
    password: str


class UserCreateUpdateModel(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    password: str