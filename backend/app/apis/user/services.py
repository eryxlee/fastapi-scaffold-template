# -*- coding: utf-8 -*-

from sqlmodel import Session, select
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import get_session
from app.commons.enums import *
from app.models.user import *


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_user_by_id(self, user_id: int = None) -> User | None:
        statement = select(User).where(User.id == user_id)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def get_user_by_name(self, username: str = None)-> User | None:
        statement = select(User).where(User.name == username)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def create_user(self, user_create: UserCreate) -> User:
        user = User(**user_create.model_dump())
        user.password = User.encrypt_password(user_create.password)
        user.is_active = UserAvailableStatus.NOT_SET
        user.is_deleted = DeleteStatus.NOT_SET

        await user.save(self.session)
        return user
