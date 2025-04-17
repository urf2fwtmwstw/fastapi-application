from typing import Annotated
from uuid import uuid4

from annotated_types import MaxLen, MinLen
from pydantic import UUID4, BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    user_id: UUID4
    username: str
    hashed_password: str


class UserCreateSchema(BaseModel):
    user_id: UUID4 = uuid4()
    username: Annotated[str, MinLen(3), MaxLen(20)]
    password: str


class UserUpdateSchema(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    old_password: str
    new_password: str
