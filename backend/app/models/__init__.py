# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid

from ast import Dict, Tuple
from typing import Any, Type
from datetime import datetime, UTC
from functools import partial

from collections.abc import Generator
from pydantic_core import PydanticUndefined

from sqlalchemy import text, String
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import declared_attr

from sqlmodel import create_engine
from sqlmodel.main import SQLModelMetaclass
from sqlmodel import Session, Field, SQLModel

from app.config import settings


# 采用配置变量创建数据库引擎
engine = create_engine(
    settings.MARIADB_DATABASE_URI.unicode_string(),
    echo=settings.DB_ENABLE_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_OVERFLOW,
    poolclass=QueuePool
)


def get_db() -> Generator[Session, None, None]:
    """ 获取数据库访问 Session"""
    with Session(engine, autocommit=False, autoflush=False) as session:
        yield session


def init_db() -> None:
    """ 初始化数据库 """
    SQLModel.metadata.create_all(engine)


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


class TableBase(SQLModel, metaclass=DescriptionMeta):
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

    def save(self, db:Session):
        db.add(self)
        self.commit_or_rollback(db)
        db.refresh(self)
        return self

    def delete(self, db:Session, commit:bool=True):
        db.session.delete(self)
        if commit:
            self.commit_or_rollback(db)

    def update(self, db:Session, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            self.commit_or_rollback(db)
        return required_commit

    @classmethod
    def add_or_update(self, db:Session, where, **kwargs):
        record = self.query.filter_by(**where).first()
        if record:
            record.update(db, **kwargs)
        else:
            record = self(**kwargs).save(db)
        return record

    def commit_or_rollback(self, db):
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise



# class Base(DeclarativeBase):
#     """ ORM 基类"""


#     # json 输出
#     def to_json(self):
#         if hasattr(self, '__table__'):
#             return {i.name: getattr(self, i.name) for i in self.__table__.columns}
#         raise AssertionError('<%r> does not have attribute for __table__' % self)


# class CommonMixin:
#     """ 数据模型公共属性与方法"""
#     __slots__ = ()

#     is_deleted: Mapped[int | None] = \
#         mapped_column(SmallInteger, server_default=text('0'), comment="是否删除: 0 未删除 1 已删除")
#     create_time: Mapped[datetime | None] = \
#         mapped_column(insert_default=func.now(), comment="创建时间")
#     update_time: Mapped[datetime | None] = \
#         mapped_column(server_default=func.now(), onupdate=func.now(), comment="更新时间")
