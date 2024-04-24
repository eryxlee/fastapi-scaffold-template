# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import Optional, List


# 项目模型
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    completed: bool

class Todo(TodoBase):
    id: int
    completed: bool
    owner_id: int

    # class Config:
    #     orm_mode = True
