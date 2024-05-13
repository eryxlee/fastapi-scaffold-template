# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, computed_field
from sqlmodel import Field, SQLModel


class PageSchemaIn(SQLModel):
    """ 分页查询参数 """
    page: int = 1
    page_size: int = 10

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @computed_field
    @property
    def limit(self) -> int:
        return self.page_size

class PageSchemaOut(SQLModel):
    """ 分页查询参数 """
    page: int = 1
    page_size: int = 10
    total: int = 0

    @computed_field
    @property
    def pages(self) -> int:
        return (self.total - 1) // self.page_size + 1

def page_query(page: int = 1, page_size: int = 10):
    """ 获取查询参数 """
    return PageSchemaIn(page=page, page_size=page_size)


PageQuery = Annotated[PageSchemaIn, Depends(page_query)]
