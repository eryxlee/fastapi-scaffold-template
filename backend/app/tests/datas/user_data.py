import pytest
import pytest_asyncio
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import *
from app.models.role import *
from app.models.resource import *
from app.services.user import UserService

@pytest_asyncio.fixture(scope='function')
async def dataset(async_session: AsyncSession):
    """初始化数据"""
    session = async_session

    resource1 = Resource(
        name="仪表盘", level=1, pid=0, icon="VBr0B.png",
        menu_url="/dashboard", request_url="/", permission_code="")
    session.add(resource1)

    resource2 = Resource(
        name="系统管理", level=0, pid=0, icon="VBr0B.png",
        menu_url="/system/index", request_url="/system", permission_code="sys")
    session.add(resource2)

    resource3 = Resource(
        name="用户管理", level=1, pid=2, icon="VBclq.png",
        menu_url="/system/user", request_url="/user", permission_code="sys:user")
    session.add(resource3)

    resource4 = Resource(
        name="用户列表", level=2, pid=3,
        request_url="/user/list", permission_code="sys:user:list")
    session.add(resource4)

    resource5 = Resource(
        name="新增用户", level=2, pid=3,
        request_url="/user/add", permission_code="sys:user:add")
    session.add(resource5)

    resource6 = Resource(
        name="编辑用户", level=2, pid=3,
        request_url="/user/update", permission_code="sys:user:update")
    session.add(resource6)

    resource7 = Resource(
        name="角色管理", level=1, pid=2, icon="VBsBc.png",
        menu_url="/system/role", request_url="/role", permission_code="sys:role")
    session.add(resource7)

    resource8 = Resource(
        name="资源管理", level=1, pid=2, icon="VBr0B.png",
        menu_url="/system/resource", request_url="/resource", permission_code="sys:resource")
    session.add(resource8)

    resource9 = Resource(
        name="公告通知", level=1, pid=0, icon="VBr0B.png",
        menu_url="/notice", request_url="/notice", permission_code="notice")
    session.add(resource9)

    resource10 = Resource(
        name="日志记录", level=1, pid=0, icon="VBr0B.png",
        menu_url="/log", request_url="/log", permission_code="log")
    session.add(resource10)

    # 新增角色
    role_admin = Role(name="超级管理员", code="ROLE_ADMIN")
    role_admin.resources = [resource1, resource2, resource3, resource4,
                            resource5, resource6, resource7, resource8,
                            resource9, resource10]
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

@pytest_asyncio.fixture(scope="function")
async def user_to_create():
    yield UserCreate(
            email="test_client@example.com",
            name="test",
            password="123456",
            avatar="test",
            gender=1,
            phone="123456",
            role_id=1
    )


@pytest_asyncio.fixture(scope="function")
async def admin_client_header(async_client):
    admin_user = {
        "username": "admin",
        "password": "123456"
    }
    res = await async_client.post('/login', data=admin_user)
    admin_client_token = res.json()['access_token']
    yield {"Authorization": f"Bearer {admin_client_token}"}
