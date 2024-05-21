# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import EmailStr
from passlib.hash import pbkdf2_sha256

from sqlalchemy import (
    String,
    Integer,
    SmallInteger,
)
from sqlmodel import SQLModel, Field, Relationship

from . import TimestampModel, IDModel, Metadata, TableBase, CommonPropertyModel


class UserBase(SQLModel):
    """ 用户模型公共部分 """
    name: str = Field(default=None, max_length=60, nullable=False, description="用户名", sa_type=String(60))
    avatar: str = Field(default=None, max_length=128, nullable=True, description="头像", sa_type=String(128))
    email: EmailStr = Field(default=None, max_length=128, nullable=True, description="邮件", sa_type=String(128))
    gender: int = Field(default=None, nullable=True, description="性别", sa_type=SmallInteger)
    phone: str = Field(default=None, max_length=36, nullable=True, description="电话", sa_type=String(36))
    role_id: int= Field(default=None, foreign_key="role.id")


class UserCreate(UserBase):
    """ 注册时采用的用户模型 """
    password: str = Field(default=None, max_length=128, nullable=False, description="密码", sa_type=String(128))


class UserUpdate(UserCreate):
    """ 更新时采用的用户模型 """
    pass


class User(
    TimestampModel,
    CommonPropertyModel,
    UserCreate,
    IDModel,
    Metadata,
    TableBase,
    table = True):
    """ 展示用户详情信息的用户模型 """
    is_active: int = Field(default=0, nullable=True, description="是否激活", sa_type=SmallInteger)

    # 多对一关系，需要定义一个role_id字段
    role: Optional["Role"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )

    def verify_password(self, raw_password) -> bool:
        # 使用passlib验证密码
        return pbkdf2_sha256.verify(raw_password, self.password)

    @classmethod
    def encrypt_password(self, raw_password) -> str:
        return pbkdf2_sha256.hash(raw_password)


class RoleResourceLink(Metadata, table=True):
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
    resource_id: int | None = Field(default=None, foreign_key="resource.id", primary_key=True)


class RoleBase(SQLModel):
    name: str = Field(max_length=32, description="角色名称", sa_type=String(32))
    code: str = Field(max_length=32, description="角色code", sa_type=String(32))
    description: str = Field(default=None, max_length=255, nullable=True, description="描述", sa_type=String(255))


class Role(
    TimestampModel,
    CommonPropertyModel,
    RoleBase,
    IDModel,
    Metadata,
    TableBase,
    table=True):
    users: list[User] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
    resources: list["Resource"] = Relationship(
        back_populates="roles",
        link_model=RoleResourceLink,
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class ResourceBase(SQLModel):
    name: str = Field(max_length=32, description="资源名称", sa_type=String(32))
    level: int = Field(default=0, description="层级: 0 目录 1 菜单 2 权限", sa_type=SmallInteger)
    pid: int = Field(default=0, description="父节点id", sa_type=Integer)
    icon: str = Field(default=None, max_length=64, nullable=True, description="图标", sa_type=String(64))
    menu_url: str = Field(default=None, max_length=64, nullable=True, description="页面路由", sa_type=String(64))
    request_url: str = Field(default=None, max_length=64, nullable=True, description="请求url", sa_type=String(64))
    permission_code: str = Field(default=None, max_length=32, nullable=True, description="权限code", sa_type=String(32))


class Resource(
    TimestampModel,
    CommonPropertyModel,
    ResourceBase,
    IDModel,
    Metadata,
    TableBase,
    table=True):
    roles: list[Role] = Relationship(
        back_populates="resources",
        link_model=RoleResourceLink,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
