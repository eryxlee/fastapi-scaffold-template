# -*- coding: utf-8 -*-

from sqlmodel import select, func

from app.models import async_session
from app.models.user import *


async def init_data():
    """ 初始化表数据 """

    async with async_session() as session:
        # 新增预置用户
        def get_select_user_stmt(name):
            return select(func.count(User.id)).where(User.name == name)
        if await session.scalar(get_select_user_stmt("admin")) == 0:
            admin = User(name="admin", password=User.encrypt_password("123456"))
            session.add(admin)
        if await session.scalar(get_select_user_stmt("user1")) == 0:
            user1 = User(name="user1", password=User.encrypt_password("123456"))
            session.add(user1)
        if await session.scalar(get_select_user_stmt("user2")) == 0:
            user2 = User(name="user2", password=User.encrypt_password("123456"))
            session.add(user2)

        await session.commit()
