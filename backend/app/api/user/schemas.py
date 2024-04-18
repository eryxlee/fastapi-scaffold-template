# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 用户模型，用于请求和响应体
class UserBase(BaseModel):
    name: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[int] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: int
    create_time: datetime
    update_time: datetime
    is_deleted: int

    class Config:
        # from_attributes 将告诉 Pydantic 模型读取数据，即它不是一个 dict，而是一个 ORM 模型
        # https://docs.pydantic.dev/2.0/usage/models/#arbitrary-class-instances
        from_attributes=True
        # 自定义编码器
        json_encoders={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
