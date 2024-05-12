# -*- coding: utf-8 -*-

from fastapi import Depends
from sqlmodel import select

from app.models import get_session, Session
from app.commons.enums import *
from app.models.user import *


class UserService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get(self, id: int = None) -> User | None:
        return User.get(self.session, id)

    async def create(self, user_create: UserCreate) -> User:
        user = User(**user_create.model_dump())
        user.password = User.encrypt_password(user_create.password)
        user.is_active = UserAvailableStatus.NOT_SET
        user.is_deleted = DeleteStatus.NOT_SET

        await user.save(self.session)
        return user

    async def patch(self, id: int, data: UserUpdate) -> User:
        user = await self.get(id=id)
        values = data.model_dump(exclude_unset=True)

        user.update(self.session, **values)
        return user

    async def delete(self, id: int) -> bool:
        await User.delete_without_select(self.session, User, id)
        return True

    async def get_user_by_name(self, username: str = None)-> User | None:
        statement = select(User).where(User.name == username)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()
