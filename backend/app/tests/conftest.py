# -*- coding: utf-8 -*-

import os
import asyncio
import pytest
import pytest_asyncio

from typing import Generator
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from collections.abc import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as Session

base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(f"{base_path}/.env", override=True) # TODO 暂时用.env
from app.config import settings


# @pytest.fixture(scope="session", autouse=True)
# def event_loop(request) -> Generator:  # noqa: indirect usage
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def testing_db():
    """创建测试数据库, 并在测试结束时删除
    测试数据库名字为 pytest_ + 原库名
    TODO 因sqlalchemy_utils 不支持异步操作，这里暂且使用同步方式
    """
    settings.DB_DATABASE = "pytest_" + settings.DB_DATABASE
    sqlalchemy_database_uri = settings.MARIADB_DATABASE_URI.unicode_string()

    if database_exists(sqlalchemy_database_uri):
        drop_database(sqlalchemy_database_uri)

    create_database(sqlalchemy_database_uri)

    yield

    drop_database(sqlalchemy_database_uri)


@pytest_asyncio.fixture(scope="session")
async def project_root_path(request):
    """pytest根目录"""
    yield request.config.rootpath


@pytest_asyncio.fixture(scope="session")
async def api_prefix():
    """API 前缀"""
    yield settings.API_PREFIX


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """创建数据库引擎"""
    return create_async_engine(
        settings.AIO_MARIADB_DATABASE_URI.unicode_string(),
        echo=settings.DB_ENABLE_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_POOL_OVERFLOW,
        future=True
    )


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[Session, None, None]:
    """创建数据库访问session, 并在每次调用前后创建、删除所有数据表"""
    session = sessionmaker(
        async_engine, class_=Session, expire_on_commit=False
    )

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(async_session):
    """创建HTTP访问客户端"""
    from app.main import app
    from app.models import get_session
    app.dependency_overrides[get_session] = lambda: async_session
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=f"http://localhost:{settings.PORT}"
    ) as client:
        yield client
