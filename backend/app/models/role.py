# -*- coding: utf-8 -*-

from sqlmodel import Field, Relationship, SQLModel, String

from ..extensions.fastapi.model import CommonPropertyModel, IDModel, Metadata, TimestampModel


class RoleResourceLink(Metadata, table=True):
    """角色-资源关联模型."""

    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
    resource_id: int | None = Field(default=None, foreign_key="resource.id", primary_key=True)


class RoleBase(SQLModel):
    """角色基础模型."""

    name: str = Field(max_length=32, description="角色名称", sa_type=String(32))
    code: str = Field(max_length=32, description="角色code", sa_type=String(32))
    description: str = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="描述",
        sa_type=String(255),
    )


class Role(TimestampModel, CommonPropertyModel, RoleBase, IDModel, Metadata, table=True):
    """角色模型."""

    users: list["User"] = Relationship(  # noqa: F821
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
    resources: list["Resource"] = Relationship(  # noqa: F821
        back_populates="roles",
        link_model=RoleResourceLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
