# -*- coding: utf-8 -*-

from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.models.user import *
from app.extensions.fastapi.pagination import PageQuery
from app.extensions.jwt import create_access_token, check_jwt_token

from .services import UserService
from .exception import *

router = APIRouter()


@router.post("/signup")
async def user_signup(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService),
) -> User:
    """ 注册新用户"""
    existing_user = await user_service.get_user_by_name(user_data.name)  # 获取用户信息
    if existing_user:
        raise UsernameUsedException()

    user_obj = await user_service.create_user(user_data)
    return user_obj


@router.post("/login")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(UserService),
) -> dict:
    try:
        existing_user = await user_service.get_user_by_name(form_data.username)
        if existing_user:
            assert existing_user.verify_password(form_data.password)
        else:
            raise UserNotFoundException()
    except AssertionError:
        raise UserOrPasswordException()

    # 过期时间
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRED)
    # 把id进行username加密，要使用str类型
    access_token = create_access_token(
        data={"sub": existing_user.name}, expires_delta=access_token_expires
    )

    # 返回一个定制的响应体以适配JWT需求
    return {"status": True, "code": 200, "message":"",
            "access_token": access_token, "token_type": "bearer"
        }


@router.get("/me", response_model=User, response_model_exclude=("password"))
def user_me(user: User = Depends(check_jwt_token)):
    """ 获取用户详情 """
    return user


@router.get("/list", dependencies=[Depends(check_jwt_token)])
def users(
    page: PageQuery = None,
    name: str | None = None,
    user_service: UserService = Depends(UserService)
):
    """ 获取用户列表 """
    a = page.page
    return None
