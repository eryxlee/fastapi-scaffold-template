# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid
from ast import Dict, Tuple  # noqa: TCH003
from datetime import UTC, datetime
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Type
from typing import Dict as DictType

from pydantic import ConfigDict, model_serializer
from pydantic.alias_generators import to_camel
from pydantic_core import PydanticUndefined
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel, String, text
from sqlmodel.main import SQLModelMetaclass

if TYPE_CHECKING:
    from fastapi.types import IncEx


class UUIDModel(SQLModel):
    """UID主键模型定义."""

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        max_length=36,
        primary_key=True,
        index=True,
        nullable=False,
        description="UID主键",
        sa_type=String(36),  # 需要制定数据库字段长度，max_length不会设置数据库字段长度
        sa_column_kwargs={"server_default": text("UUID()")},
    )


class IDModel(SQLModel):
    """自增ID主键模型定义."""

    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False,
        description="ID主键",
    )


class TimestampModel(SQLModel):
    """时间公共字段模型定义."""

    create_time: datetime = Field(
        default_factory=partial(datetime.now, UTC),
        nullable=False,
        description="创建时间",
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )

    update_time: datetime = Field(
        default_factory=partial(datetime.now, UTC),
        nullable=False,
        description="更新时间",
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")},
    )


class CommonPropertyModel(SQLModel):
    """其他公共字段模型定义."""

    is_deleted: bool = Field(default=False, nullable=False, description="是否已删除")


# Automatically set comment to Column using description.
# https://github.com/tiangolo/sqlmodel/issues/492
class DescriptionMeta(SQLModelMetaclass):
    """将 description作为字段的comment."""

    def __new__(  # noqa: D102
        cls,
        name: str,
        bases: Tuple[Type[Any], ...],  # noqa: UP006
        class_dict: Dict[str, Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
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
                if field.sa_column is not PydanticUndefined and not field.sa_column.comment:
                    field.sa_column.comment = desc
                # deal with attributes of new_class
                if hasattr(new_class, k):
                    column = getattr(new_class, k)
                    if hasattr(column, "comment") and not column.comment:
                        column.comment = desc
        return new_class


class Metadata(SQLModel, metaclass=DescriptionMeta):
    """数据库表公共属性模型定义."""

    __table_args__: ClassVar[dict[str, str]] = {
        "mysql_engine": "InnoDB",  # MySQL引擎
        "mysql_charset": "utf8mb4",  # 设置表的字符集
        "mysql_collate": "utf8mb4_general_ci",  # 设置表的校对集
    }

    # https://blog.csdn.net/mouday/article/details/90079956
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """类名转表名."""
        snake_case = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", cls.__name__)
        return snake_case.lower().strip("_")


class SortModel(SQLModel):
    """支持模型json序列化的时候按照key进行排序."""

    @model_serializer(when_used="json")
    def sort_model(self) -> DictType[str, Any]:  # noqa: UP006
        """按照key进行排序."""
        return dict(sorted(self.model_dump().items()))


class DatetimeFormatModel(SQLModel):
    """日期格式化."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")})


class PublicBaseModel(SQLModel):
    """输出模型公共部分."""

    id: int
    create_time: datetime
    update_time: datetime


class AliasCamelModel(SQLModel):
    """输出Key蛇形命名转驼峰."""

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        """Generate a dictionary representation of the model."""
        return self.__pydantic_serializer__.to_python(
            self,
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=True,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=True,
            round_trip=round_trip,
            warnings=warnings,
        )

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
