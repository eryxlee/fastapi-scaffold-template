# -*- coding: utf-8 -*-

from typing import List

from fastapi import Depends
from sqlmodel import func, select

from ..models import Session, get_session
from ..models.role import Role


class RoleService:
    """角色管理业务逻辑类."""

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get_role_list_count(self) -> int:
        """检索角色列表计数."""
        count_statement = select(func.count()).select_from(Role)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_role_list(self, offset, limit) -> List[Role] | None:
        """检索角色列表."""
        statement = select(Role).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
