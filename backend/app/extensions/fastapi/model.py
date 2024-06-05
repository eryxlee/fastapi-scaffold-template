# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid

from ast import Dict, Tuple
from typing import Any, Type
from functools import partial
from datetime import datetime, UTC
from pydantic_core import PydanticUndefined

from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, text, String
from sqlmodel.main import SQLModelMetaclass


class UUIDModel(SQLModel):
    """ UID主键模型定义 """
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        max_length=36,
        primary_key=True,
        index=True,
        nullable=False,
        description="UID主键",
        sa_type=String(36),  # 需要制定数据库字段长度，max_length不会设置数据库字段长度
        sa_column_kwargs={
            "server_default": text("UUID()")
        }
    )


class IDModel(SQLModel):
    """ 自增ID主键模型定义 """
    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False,
        description="ID主键"
    )


class TimestampModel(SQLModel):
    """ 时间公共字段模型定义 """
    create_time: datetime = Field(
        default_factory=partial(datetime.now, UTC),
        nullable=False,
        description="创建时间",
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP")
        }
    )

    update_time: datetime = Field(
        default_factory=partial(datetime.now, UTC),
        nullable=False,
        description="更新时间",
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        }
    )


class CommonPropertyModel(SQLModel):
    """ 其他公共字段模型定义 """
    is_deleted: bool = Field(
        default=False,
        nullable=False,
        description="是否已删除"
    )


# Automatically set comment to Column using description.
# https://github.com/tiangolo/sqlmodel/issues/492
class DescriptionMeta(SQLModelMetaclass):
    """ 将 description作为字段的comment """
    def __new__(
        cls,
        name: str,
        bases: Tuple[Type[Any], ...],
        class_dict: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        new_class = super().__new__(cls, name, bases, class_dict, **kwargs)
        fields = new_class.model_fields
        for k, field in fields.items():
            desc = field.description
            if desc:
                # deal with sa_column_kwargs
                if field.sa_column_kwargs is not PydanticUndefined:
                    field.sa_column_kwargs["comment"] = desc
                else:
                    field.sa_column_kwargs = {"comment": desc}
                # deal with sa_column
                if field.sa_column is not PydanticUndefined:
                    if not field.sa_column.comment:
                        field.sa_column.comment = desc
                # deal with attributes of new_class
                if hasattr(new_class, k):
                    column = getattr(new_class, k)
                    if hasattr(column, "comment") and not column.comment:
                        column.comment = desc
        return new_class


class Metadata(SQLModel, metaclass=DescriptionMeta):
    """ 数据库表公共属性模型定义 """
    __table_args__ = {
        "mysql_engine": "InnoDB",  # MySQL引擎
        "mysql_charset": "utf8mb4",  # 设置表的字符集
        "mysql_collate": "utf8mb4_general_ci",  # 设置表的校对集
    }

    # 类名转表名
    # https://blog.csdn.net/mouday/article/details/90079956
    @declared_attr.directive
    def __tablename__(cls) -> str:
        snake_case = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", cls.__name__)
        return snake_case.lower().strip('_')
