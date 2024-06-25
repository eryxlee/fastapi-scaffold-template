# -*- coding: utf-8 -*-

from typing import Annotated

from fastapi import Depends
from pydantic import computed_field

from .model import AliasCamelModel


class PageModel(AliasCamelModel):
    """分页查询参数."""

    page: int = 1
    page_size: int = 10
    total: int | None = None

    # computed_field decorator to include property and
    # cached_property when serializing models or dataclasses.
    # if don't want to include (= exclude) a field we
    # shouldn't use computed_field decorator
    # @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    # 如果不希望出现在序列化结果中，就不要加computed_field
    # @computed_field
    @property
    def limit(self) -> int:
        return self.page_size

    @computed_field
    @property
    def pages(self) -> int:
        return (self.total - 1) // self.page_size + 1


def page_query(page: int = 1, page_size: int = 10):
    """获取查询参数."""
    return PageModel(page=page, page_size=page_size)


PageQueryParam = Annotated[PageModel, Depends(page_query)]
