# -*- coding: utf-8 -*-

import pkgutil
from importlib import import_module
from fastapi import APIRouter

api_router = APIRouter()
base_router = APIRouter()

# 导入所有的子模块
for module in pkgutil.iter_modules(['app/apis']):
    if not module.ispkg:
        continue

    sub_api = import_module(f'app.apis.{module.name}')
    api_router.include_router(sub_api.router, prefix=f"/{module.name}", tags=[module.name])


from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.models.user import *
from app.extensions.jwt import create_access_token

from app.services.user import UserService
from app.apis.user.exception import *

@base_router.get("/")
async def hello():
    return {"message": "Hello, FastAPI!"}


@base_router.post("/login")
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
