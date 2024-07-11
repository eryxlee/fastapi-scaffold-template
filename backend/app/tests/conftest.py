# -*- coding: utf-8 -*-

import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as Session

# @pytest.fixture(scope="session", autouse=True)
# def event_loop(request):
#     """Replacing the event_loop fixture with a custom implementation is deprecated
#     and will lead to errors in the future.
#     If you want to request an asyncio event loop with a scope other than function
#     scope, use the "scope" argument to the asyncio mark when marking the tests.
#     If you want to return different types of event loops, use the event_loop_policy
#     fixture."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def application():
    """应用app."""
    from app.main import app

    yield app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def app_settings():
    """应用配置信息."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(f"{base_path}/.env", override=True)  # TODO 暂时用.env
    from app.config import settings

    yield settings


@pytest_asyncio.fixture(scope="session", autouse=True)
async def project_root_path(request):
    """pytest根目录."""
    yield request.config.rootpath


@pytest_asyncio.fixture(scope="session", autouse=True)
async def api_prefix(app_settings):
    """API 前缀."""
    yield app_settings.API_PREFIX


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_testing_db(app_settings):
    """创建测试数据库并在测试结束时删除.

    测试数据库名字为 pytest_ + 原库名 TODO 因sqlalchemy_utils 不支持异步操作，这里暂且使用同步方式.
    """
    app_settings.DB_DATABASE = "pytest_" + app_settings.DB_DATABASE
    sqlalchemy_database_uri = app_settings.MARIADB_DATABASE_URI.unicode_string()

    if database_exists(sqlalchemy_database_uri):
        drop_database(sqlalchemy_database_uri)

    create_database(sqlalchemy_database_uri)

    yield

    drop_database(sqlalchemy_database_uri)


@pytest_asyncio.fixture(scope="session")
async def async_engine(app_settings):
    """创建数据库引擎."""
    return create_async_engine(
        app_settings.AIO_MARIADB_DATABASE_URI.unicode_string(),
        echo=app_settings.DB_ENABLE_ECHO,
        pool_size=app_settings.DB_POOL_SIZE,
        max_overflow=app_settings.DB_POOL_OVERFLOW,
        future=True,
    )


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[Session, None, None]:
    """创建数据库访问session, 并在每次调用前后创建、删除所有数据表."""
    session = sessionmaker(async_engine, class_=Session, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(async_session, app_settings):
    """创建HTTP访问客户端."""
    from app.main import app
    from app.models import get_session

    app.dependency_overrides[get_session] = lambda: async_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://localhost:{app_settings.PORT}",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def setup_redis_cache(app_settings):
    """构建redis cache."""
    from ..models.redis import build_redis_cache

    async with build_redis_cache(app_settings):
        yield


@pytest_asyncio.fixture(scope="function")
async def setup_initial_dataset(async_session: Session):
    """初始化数据."""
    from ..models.resource import Resource
    from ..models.role import Role
    from ..models.user import User

    session = async_session

    resource1 = Resource(
        name="仪表盘",
        level=1,
        pid=0,
        icon="VBr0B.png",
        menu_url="/dashboard",
        request_url="/",
        permission_code="",
    )
    session.add(resource1)

    resource2 = Resource(
        name="系统管理",
        level=0,
        pid=0,
        icon="VBr0B.png",
        menu_url="/system/index",
        request_url="/system",
        permission_code="sys",
    )
    session.add(resource2)

    resource3 = Resource(
        name="用户管理",
        level=1,
        pid=2,
        icon="VBclq.png",
        menu_url="/system/user",
        request_url="/user",
        permission_code="sys:user",
    )
    session.add(resource3)

    resource4 = Resource(
        name="用户列表",
        level=2,
        pid=3,
        request_url="/user/list",
        permission_code="sys:user:list",
    )
    session.add(resource4)

    resource5 = Resource(
        name="新增用户",
        level=2,
        pid=3,
        request_url="/user/add",
        permission_code="sys:user:add",
    )
    session.add(resource5)

    resource6 = Resource(
        name="编辑用户",
        level=2,
        pid=3,
        request_url="/user/update",
        permission_code="sys:user:update",
    )
    session.add(resource6)

    resource7 = Resource(
        name="角色管理",
        level=1,
        pid=2,
        icon="VBsBc.png",
        menu_url="/system/role",
        request_url="/role",
        permission_code="sys:role",
    )
    session.add(resource7)

    resource8 = Resource(
        name="资源管理",
        level=1,
        pid=2,
        icon="VBr0B.png",
        menu_url="/system/resource",
        request_url="/resource",
        permission_code="sys:resource",
    )
    session.add(resource8)

    resource9 = Resource(
        name="公告通知",
        level=1,
        pid=0,
        icon="VBr0B.png",
        menu_url="/notice",
        request_url="/notice",
        permission_code="notice",
    )
    session.add(resource9)

    resource10 = Resource(
        name="日志记录",
        level=1,
        pid=0,
        icon="VBr0B.png",
        menu_url="/log",
        request_url="/log",
        permission_code="log",
    )
    session.add(resource10)

    # 新增角色
    role_admin = Role(name="超级管理员", code="ROLE_ADMIN")
    role_admin.resources = [
        resource1,
        resource2,
        resource3,
        resource4,
        resource5,
        resource6,
        resource7,
        resource8,
        resource9,
        resource10,
    ]
    session.add(role_admin)

    role_user = Role(name="用户", code="ROLE_USER")
    role_user.resources = [resource1]
    session.add(role_user)

    role_audit = Role(name="审计员", code="ROLE_AUDIT")
    role_audit.resources = [resource1, resource10]
    session.add(role_audit)

    # 新增预置用户
    admin = User(name="admin", password=User.encrypt_password("123456"))
    admin.role = role_admin
    session.add(admin)

    user = User(name="user", password=User.encrypt_password("123456"))
    user.role = role_user
    session.add(user)

    audit = User(name="audit", password=User.encrypt_password("123456"))
    audit.role = role_audit
    session.add(audit)

    await session.commit()

    yield
