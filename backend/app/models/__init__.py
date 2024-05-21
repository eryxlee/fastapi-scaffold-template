# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid

from ast import Dict, Tuple
from typing import Any, Type, TypeVar
from functools import partial
from datetime import datetime, UTC

from collections.abc import AsyncGenerator
from pydantic_core import PydanticUndefined

from sqlalchemy import text, String
from sqlalchemy.orm import declared_attr, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from sqlmodel import SQLModel, Field, select, delete
from sqlmodel.main import SQLModelMetaclass
from sqlmodel.ext.asyncio.session import AsyncSession as Session

from app.config import settings

# 采用配置变量创建数据库引擎
async_engine = create_async_engine(
    settings.AIO_MARIADB_DATABASE_URI.unicode_string(),
    echo=settings.DB_ENABLE_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_OVERFLOW,
    future=True
)

async_session = sessionmaker(
    async_engine, class_=Session, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[Session, None, None]:
    async with async_session() as session:
        yield session


# metadata.create_all doesn't execute asynchronously, so we used run_sync
# to execute it synchronously within the async function.
async def init_db() -> None:
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


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


T = TypeVar('T')


class TableBase(SQLModel, metaclass=DescriptionMeta):
    """ 数据库表公共属性模型定义 """
    @classmethod
    async def get(cls, session:Session, T, id: int = None) -> T | None:
        statement = select(T).where(T.id == id)
        results = await session.exec(statement=statement)
        return results.one_or_none()

    async def save(self, session:Session):
        session.add(self)
        await self.commit_or_rollback(session)
        await session.refresh(self)
        return self

    async def delete(self, session:Session, commit:bool=True):
        await session.delete(self)
        if commit:
            await self.commit_or_rollback(session)

    @classmethod
    async def delete_without_select(cls, session:Session, T, id: int):
        statement = delete(T).where(T.id == id)

        await session.exec(statement=statement)
        await session.commit()

    async def update(self, session:Session, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            await self.commit_or_rollback(session)
        return required_commit

    @classmethod
    async def add_or_update(self, session:Session, where, **kwargs):
        record = session.query.filter_by(**where).first()
        if record:
            await record.update(session, **kwargs)
        else:
            record = await self(**kwargs).save(session)
        return record

    async def commit_or_rollback(self, session):
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise
