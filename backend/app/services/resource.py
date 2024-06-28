# -*- coding: utf-8 -*-

from typing import List

from fastapi import Depends
from sqlmodel import func, select

from ..models import Session, get_session
from ..models.resource import Resource


class ResourceService:
    """资源管理模块业务逻辑类."""

    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    async def get_resource_list_count(self) -> int:
        """检索资源列表计数."""
        count_statement = select(func.count()).select_from(Resource)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_resource_list(self, offset: int, limit: int) -> List[Resource] | None:
        """检索资源列表."""
        statement = select(Resource).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
