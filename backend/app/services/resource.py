# -*- coding: utf-8 -*-

from typing import List
from fastapi import Depends
from sqlmodel import func, select

from app.models import get_session, Session
from app.commons.enums import *
from app.models.resource import *


class ResourceService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get(self, id: int = None) -> Resource | None:
        return await Resource.get(self.session, Resource, id)

    async def get_resource_list_count(self)-> int:
        count_statement = select(func.count()).select_from(Resource)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_resource_list(self, offset, limit)-> List[Resource] | None:
        statement = select(Resource).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
