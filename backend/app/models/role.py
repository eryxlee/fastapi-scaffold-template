# -*- coding: utf-8 -*-

from typing import List, Optional

from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    String,
)

from app.extensions.fastapi.pagination import PageSchemaOut
from . import (
    TimestampModel,
    IDModel,
    Metadata,
    TableBase,
    CommonPropertyModel
)



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
    users: list["User"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
    resources: list["Resource"] = Relationship(
        back_populates="roles",
        link_model=RoleResourceLink,
        sa_relationship_kwargs={"lazy": "selectin"}
    )


