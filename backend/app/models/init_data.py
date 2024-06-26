# -*- coding: utf-8 -*-

from sqlmodel import func, select

from . import async_session, init_db
from .resource import Resource
from .role import Role
from .user import User


async def init_data():  # noqa: C901
    """初始化表数据."""
    await init_db()

    async with async_session() as session:
        # 新增资源

        def get_select_resource_stmt(name):
            return select(func.count(Resource.id)).where(Resource.name == name)

        resource1 = resource2 = resource3 = resource4 = resource5 = None
        resource6 = resource7 = resource8 = resource9 = resource10 = None
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource1)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource2)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource3)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
            resource4 = Resource(
                name="用户列表",
                level=2,
                pid=3,
                request_url="/user/list",
                permission_code="sys:user:list",
            )
            session.add(resource4)
            session.refresh(resource4)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
            resource5 = Resource(
                name="新增用户",
                level=2,
                pid=3,
                request_url="/user/add",
                permission_code="sys:user:add",
            )
            session.add(resource5)
            session.refresh(resource5)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
            resource6 = Resource(
                name="编辑用户",
                level=2,
                pid=3,
                request_url="/user/update",
                permission_code="sys:user:update",
            )
            session.add(resource6)
            session.refresh(resource6)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource7)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource8)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource9)
        if await session.scalar(get_select_resource_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(resource10)

        # 新增角色
        def get_select_role_stmt(code):
            return select(func.count(Role.id)).where(Role.code == code)

        role_admin = role_user = role_audit = None
        if await session.scalar(get_select_role_stmt("ROLE_ADMIN")) == 0:
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
            session.refresh(role_admin)
        if await session.scalar(get_select_role_stmt("ROLE_USER")) == 0:
            role_user = Role(name="用户", code="ROLE_USER")
            role_user.resources = [resource1]
            session.add(role_user)
            session.refresh(role_user)
        if await session.scalar(get_select_role_stmt("ROLE_AUDIT")) == 0:
            role_audit = Role(name="审计员", code="ROLE_AUDIT")
            role_audit.resources = [resource1, resource10]
            session.add(role_audit)
            session.refresh(role_audit)

        # 新增预置用户
        def get_select_user_stmt(name):
            return select(func.count(User.id)).where(User.name == name)

        if await session.scalar(get_select_user_stmt("admin")) == 0:
            admin = User(name="admin", password=User.encrypt_password("123456"))
            admin.role = role_admin
            session.add(admin)
        if await session.scalar(get_select_user_stmt("user")) == 0:
            user = User(name="user", password=User.encrypt_password("123456"))
            user.role = role_user
            session.add(user)
        if await session.scalar(get_select_user_stmt("user2")) == 0:
            audit = User(name="audit", password=User.encrypt_password("123456"))
            audit.role = role_audit
            session.add(audit)

        await session.commit()
