# -*- coding: utf-8 -*-

from collections.abc import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as Session

from app.config import settings
from app.models.user import *
from app.models.role import *
from app.models.resource import *


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
