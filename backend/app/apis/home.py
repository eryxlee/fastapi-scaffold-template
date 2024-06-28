# -*- coding: utf-8 -*-

from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..apis.user.exception import UserNotFoundException, UserOrPasswordErrorException
from ..config import settings
from ..extensions.auth import create_access_token
from ..services.user import UserService

# 定制一个不带api prefix的api router，将一些随业务变动不大的api放这里
base_router = APIRouter()


@base_router.get("/")
async def helth_check() -> dict:
    """心跳检查."""
    return {"message": "Hello, FastAPI!"}


@base_router.post("/login")
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(UserService),
) -> dict:
    """使用请求表单进行用户登录."""
    existing_user = await user_service.get_user_by_name(form_data.username)
    if existing_user:
        if not existing_user.verify_password(form_data.password):
            raise UserOrPasswordErrorException
    else:
        raise UserNotFoundException

    # 过期时间
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRED)
    # 把id进行username加密，要使用str类型
    access_token = create_access_token(
        data={"sub": existing_user.name},
        expires_delta=access_token_expires,
    )

    # 返回一个定制的响应体以适配JWT需求
    return {
        "status": True,
        "code": 200,
        "message": "",
        "access_token": access_token,
        "token_type": "bearer",
    }
