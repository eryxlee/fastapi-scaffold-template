# -*- coding: utf-8 -*-

from datetime import timedelta
from sqlalchemy.orm import Session
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.models import get_db, user
from app.apis.user import schemas
from app.extensions.fastapi.pagination import PageQuery
from app.extensions.jwt import create_access_token, check_jwt_token

from . import services as user_service


router = APIRouter()

@router.post("/signup")
async def user_signup(user_data: schemas.UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> schemas.UserOut:
    """ 注册新用户"""
    existing_user = user_service.get_user_by_name(db, user_data.name)  # 获取用户信息
    t = settings.MARIADB_DATABASE_URI.unicode_string()
    if existing_user:
        print(existing_user.name)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Name already registered")

    user_obj = user_service.create_user(db, user_data)
    return schemas.UserOut.model_validate(user_obj)


@router.post("/login")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        existing_user = user_service.get_user_by_name(db, form_data.username)
        if existing_user:
            assert existing_user.verify_password(form_data.password)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")
    except AssertionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")

    # 过期时间
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRED)
    # 把id进行username加密，要使用str类型
    access_token = create_access_token(
        data={"sub": existing_user.name}, expires_delta=access_token_expires
    )

    token_out = schemas.TokenModel.model_validate(existing_user, from_attributes=True)
    token_out.token = access_token

    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me")
def user_me(user: user.User = Depends(check_jwt_token)):
    """ 获取用户详情 """
    return user


@router.get("/list", dependencies=[Depends(check_jwt_token)])
def users(db: Session = Depends(get_db), page: PageQuery = None, name: str | None = None):
    """ 获取用户列表 """
    a = page.page
    return None
