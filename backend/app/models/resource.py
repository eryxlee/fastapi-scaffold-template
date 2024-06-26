# -*- coding: utf-8 -*-


from sqlmodel import Field, Integer, Relationship, SmallInteger, SQLModel, String

from ..extensions.fastapi.model import CommonPropertyModel, IDModel, Metadata, TimestampModel
from .role import Role, RoleResourceLink


class ResourceBase(SQLModel):
    """资源基础模型."""

    name: str = Field(max_length=32, description="资源名称", sa_type=String(32))
    level: int = Field(default=0, description="层级: 0 目录 1 菜单 2 权限", sa_type=SmallInteger)
    pid: int = Field(default=0, description="父节点id", sa_type=Integer)
    icon: str = Field(
        default=None,
        max_length=64,
        nullable=True,
        description="图标",
        sa_type=String(64),
    )
    menu_url: str = Field(
        default=None,
        max_length=64,
        nullable=True,
        description="页面路由",
        sa_type=String(64),
    )
    request_url: str = Field(
        default=None,
        max_length=64,
        nullable=True,
        description="请求url",
        sa_type=String(64),
    )
    permission_code: str = Field(
        default=None,
        max_length=32,
        nullable=True,
        description="权限code",
        sa_type=String(32),
    )


class Resource(TimestampModel, CommonPropertyModel, ResourceBase, IDModel, Metadata, table=True):
    """资源模型."""

    roles: list[Role] = Relationship(
        back_populates="resources",
        link_model=RoleResourceLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
