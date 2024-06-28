# -*- coding: utf-8 -*-

from typing import List, Optional

import bcrypt
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SmallInteger, SQLModel, String

from ..extensions.fastapi.model import (
    AliasCamelModel,
    CommonPropertyModel,
    DatetimeFormatModel,
    IDModel,
    Metadata,
    PublicBaseModel,
    SortModel,
    TimestampModel,
)
from ..extensions.fastapi.pagination import PageModel


class UserBase(SQLModel):
    """用户模型公共部分."""

    name: str = Field(
        default=None,
        max_length=60,
        nullable=False,
        description="用户名",
        sa_type=String(60),
    )
    avatar: str | None = Field(
        default=None,
        max_length=128,
        nullable=True,
        description="头像",
        sa_type=String(128),
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=128,
        nullable=True,
        description="邮件",
        sa_type=String(128),
    )
    gender: int | None = Field(
        default=None,
        nullable=True,
        description="性别",
        sa_type=SmallInteger,
    )
    phone: str | None = Field(
        default=None,
        max_length=36,
        nullable=True,
        description="电话",
        sa_type=String(36),
    )
    role_id: int = Field(default=None, foreign_key="role.id")


class UserCreate(UserBase):
    """注册时采用的用户模型."""

    password: str = Field(
        default=None,
        max_length=128,
        nullable=False,
        description="密码",
        sa_type=String(128),
    )


class UserUpdate(UserCreate):
    """更新时采用的用户模型."""


class UserPublic(
    UserBase,
    PublicBaseModel,
    SortModel,
    DatetimeFormatModel,
    AliasCamelModel,
):
    """展示用户信息的模型."""

    is_active: int


class User(TimestampModel, CommonPropertyModel, UserCreate, IDModel, Metadata, table=True):
    """用户详情信息的用户模型."""

    is_active: int = Field(default=0, nullable=True, description="是否激活", sa_type=SmallInteger)

    # 多对一关系，需要定义一个role_id字段
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    def verify_password(self, raw_password: str) -> bool:
        """密码验证."""
        if isinstance(raw_password, str):
            raw_password = raw_password.encode()
        return bcrypt.checkpw(raw_password, self.password.encode())

    @classmethod
    def encrypt_password(cls, raw_password: str) -> str:
        """密码加密."""
        return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt(12)).decode()


class UserListPage(SQLModel):
    """API输出用户列表模型, 忽略密码."""

    users: List[UserPublic]
    page: PageModel


class Token(SQLModel):
    """JWT Token模型."""

    access_token: str
    token_type: str
