# -*- coding: utf-8 -*-

from typing import Optional, List
from pydantic import BaseModel, Field

from app.extensions.pydantic.schema import CommonSchemaMixin


# 用户模型，用于请求和响应体
class UserBase(BaseModel):
    """ 用户模型公共部分 """
    name: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[int] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """ 注册时采用的用户模型 """
    password: str


class UserUpdate(UserCreate):
    """ 更新时采用的用户模型 """
    pass


class UserOut(UserBase, CommonSchemaMixin):
    """ 展示用户详情信息的用户模型 """
    is_active: int
    is_deleted: int


class UserLogin(BaseModel):
    """ 用户登录时的数据模型 """
    name: str = Field(example='用户名')
    password: str = Field(example='密码')

class TokenModel(UserBase):
    token: str = None