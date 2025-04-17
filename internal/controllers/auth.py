from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.auth import utils
from internal.auth.repository.users import UsersRepository
from internal.databases.database import get_db
from internal.schemas.token_schema import TokenInfo
from internal.schemas.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema
from internal.services.user_service import UserService

resources = {}


@asynccontextmanager
async def lifespan(router: APIRouter):
    resources["user_repository"] = UsersRepository()
    resources["user_service"] = UserService(resources["user_repository"])
    yield
    resources.clear()


router = APIRouter(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/signin")


def get_user_service():
    user_service = resources.get("user_service", None)
    if user_service is None:
        raise ModuleNotFoundError('"user_service" was not initialized')
    return user_service


async def validate_auth_user(
    service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    username: str = Form(),
    password: str = Form(),
) -> UserSchema:
    unauthorised_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
    )

    if not (user := await service.get_user(db, username)):
        raise unauthorised_exc

    if utils.validate_password(password, hashed_password=user.hashed_password):
        return user
    raise unauthorised_exc


async def get_auth_user_info(
    service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    token: str = Depends(oauth2_scheme),
) -> UserSchema:
    try:
        payload = utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    username: str | None = payload.get("username")

    if user := await service.get_user(db, username):
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    )


@router.post("/signup", status_code=HTTPStatus.CREATED, response_model=TokenInfo)
async def auth_new_user_issue_jwt(
    user_data: UserCreateSchema,
    service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TokenInfo:
    await service.add_user(db, user_data)
    jwt_payload: dict = {"sub": str(user_data.user_id), "username": user_data.username}
    token = utils.encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="Bearer")


@router.post("/signin", response_model=TokenInfo)
async def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
) -> TokenInfo:
    jwt_payload: dict = {
        "sub": str(user.user_id),
        "username": user.username,
    }
    token = utils.encode_jwt(jwt_payload)

    return TokenInfo(access_token=token, token_type="Bearer")


@router.get("/verify")
def view_auth_user_info(user: UserSchema = Depends(get_auth_user_info)) -> dict:
    return {
        "user_id": user.user_id,
        "username": user.username,
    }


@router.patch("/users/{user_id}", response_model=TokenInfo)
async def update_auth_user_data(
    user_data: UserUpdateSchema,
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TokenInfo:
    await service.update_user(
        db,
        user_id,
        data=user_data,
    )
    jwt_payload: dict = {
        "sub": user_id,
        "username": user_data.username,
    }
    token = utils.encode_jwt(jwt_payload)

    return TokenInfo(access_token=token, token_type="Bearer")
