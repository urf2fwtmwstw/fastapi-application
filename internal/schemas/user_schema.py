from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import UUID4, BaseModel, ConfigDict


class UserModel(BaseModel):
    model_config = ConfigDict(strict=True)

    user_id: UUID4
    username: str
    password: str

class UserCreateModel(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    password: str

class UserUpdateModel(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    old_password: str
    new_password: str