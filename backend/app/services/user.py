# -*- coding: utf-8 -*-

from typing import Optional

from fastapi import Depends
from sqlmodel import func, select

from ..commons.enums import DeleteStatus, UserAvailableStatus
from ..extensions.fastapi.service import ServiceBase
from ..models import Session, get_session
from ..models.user import User, UserCreate, UserUpdate


class UserService(ServiceBase[User]):
    """用户管理模块业务逻辑."""

    def __init__(self, session: Session = Depends(get_session)) -> None:
        super().__init__(User, session)

    async def create(self, user_create: UserCreate) -> User:
        """创建用户."""
        user = User.model_validate(
            user_create,
            update={
                "password": User.encrypt_password(user_create.password),
                "is_active": UserAvailableStatus.NOT_SET,
                "is_deleted": DeleteStatus.NOT_SET,
            },
        )

        await self.save(user)
        return user

    async def patch_by_obj(self, target_user: User, data: UserUpdate) -> User:
        """通过已有用户对象修改部分用户信息."""
        values = data.model_dump(exclude_unset=True)

        if "password" in values:
            password = values["password"]
            hashed_password = User.encrypt_password(password)
            values["password"] = hashed_password

        await self.update(target_user, **values)
        return target_user

    async def patch(self, id_: int, data: UserUpdate) -> User:
        """通过用户ID修改部分用户信息."""
        user = await self.get(id=id_)
        values = data.model_dump(exclude_unset=True)

        if "password" in values:
            password = values["password"]
            hashed_password = User.encrypt_password(password)
            values["password"] = hashed_password

        await self.update(user, **values)
        return user

    async def get_user_by_name(self, username: Optional[str] = None) -> User | None:
        """通过用户名检索用户."""
        statement = select(User).where(User.name == username)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def get_user_list_count(self) -> int:
        """检索用户列表计数."""
        count_statement = select(func.count()).select_from(User)
        result = await self.session.exec(count_statement)
        return result.one()

    async def get_user_list(self, offset: int, limit: int) -> User | None:
        """检索用户列表."""
        statement = select(User).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        return result.all()
