# -*- coding: utf-8 -*-

from typing import List
from fastapi import Depends
from sqlmodel import func, select

from app.models import get_session, Session
from app.commons.enums import *
from app.models.role import *


class RoleService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get(self, id: int = None) -> Role | None:
        return await Role.get(self.session, Role, id)

    async def get_role_list_count(self)-> int:
        count_statement = select(func.count()).select_from(Role)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_role_list(self, offset, limit)-> List[Role] | None:
        statement = select(Role).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
