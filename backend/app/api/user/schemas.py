from pydantic import BaseModel, Field
from typing import Optional, List

# 用户模型，用于请求和响应体
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    # created_at: Optional[str] = None
    # updated_at: Optional[str] = None

    # class Config:
    #     orm_mode = True

