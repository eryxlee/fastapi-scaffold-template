# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.models import get_db, user
from app.apis.user import schemas
from app.extensions.fastapi.pagination import PageQuery

from . import services as user_service


router = APIRouter()

@router.post("/signup")
async def user_signup(user_data: schemas.UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> schemas.UserOut:
    """ 注册新用户"""
    existing_user = user_service.get_user_by_name(db, user_data.name)  # 获取用户信息
    if existing_user:
        print(existing_user.name)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Name already registered")

    user_obj = user_service.create_user(db, user_data)
    return schemas.UserOut.model_validate(user_obj)


@router.post("/login")
async def user_login(user_data: schemas.UserLogin,
    response: Response,
    db: Session = Depends(get_db),
) -> schemas.UserOut:
    try:
        existing_user = user_service.get_user_by_name(db, user_data.name)
        if existing_user:
            assert existing_user.verify_password(user_data.password)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")
    except AssertionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")

    return schemas.UserOut.model_validate(existing_user)


@router.get("/list")
def users(db: Session = Depends(get_db), page: PageQuery = None, name: str | None = None):
    """ 获取用户列表 """
    a = page.page
    return None




