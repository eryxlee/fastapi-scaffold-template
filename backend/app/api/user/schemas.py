from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

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
        orm_mode = True

