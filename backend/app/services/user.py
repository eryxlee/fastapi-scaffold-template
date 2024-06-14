# -*- coding: utf-8 -*-

from fastapi import Depends
from sqlmodel import func, select

from app.models import get_session, Session
from app.extensions.fastapi.service import ServiceBase
from app.commons.enums import DeleteStatus, UserAvailableStatus
from app.models.user import (
    User,
    UserCreate,
    UserUpdate,
)


class UserService(ServiceBase[User]):
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get(self, id: int = None) -> User | None:
        return await super(UserService, self).get(self.session, User, id)

    async def create(self, user_create: UserCreate) -> User:
        user = User.model_validate(
            user_create,
            update={
                "password": User.encrypt_password(user_create.password),
                "is_active": UserAvailableStatus.NOT_SET,
                "is_deleted": DeleteStatus.NOT_SET
            }
        )

        await self.save(self.session, user)
        return user

    async def patch_by_obj(self, target_user: User, data: UserUpdate) -> User:
        values = data.model_dump(exclude_unset=True)

        if "password" in values:
            password = values["password"]
            hashed_password = User.encrypt_password(password)
            values["password"] = hashed_password

        await self.update(self.session, target_user, **values)
        return target_user

    async def patch(self, id: int, data: UserUpdate) -> User:
        user = await self.get(id=id)
        values = data.model_dump(exclude_unset=True)

        if "password" in values:
            password = values["password"]
            hashed_password = User.encrypt_password(password)
            values["password"] = hashed_password

        await self.update(self.session, user, **values)
        return user

    async def delete(self, id: int) -> bool:
        await self.delete_without_select(self.session, User, id)
        return True

    async def get_user_by_name(self, username: str = None)-> User | None:
        statement = select(User).where(User.name == username)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def get_user_list_count(self)-> int:
        count_statement = select(func.count()).select_from(User)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_user_list(self, offset, limit)-> User | None:
        statement = select(User).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
