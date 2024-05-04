# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel


class PageSchemaIn(BaseModel):
    """ 分页查询参数 """
    page: int = 1
    page_size: int = 10


class PageSchemaOut(BaseModel):
    """ 分页查询参数 """
    page: int = 1
    page_size: int = 10

def page_query(page: int = 1, page_size: int = 10):
    """ 获取查询参数 """
    return PageSchemaIn(page=page, page_size=page_size)


PageQuery = Annotated[PageSchemaIn, Depends(page_query)]
