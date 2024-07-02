# -*- coding: utf-8 -*-

import pytest_asyncio


@pytest_asyncio.fixture()
async def user_payload():
    """准备用户创建测试模型."""
    from ...models.user import UserCreate

    yield UserCreate(
        email="test_client@example.com",
        name="test",
        password="123456",
        avatar="test",
        gender=1,
        phone="15800001111",
        role_id=1,
    )


@pytest_asyncio.fixture()
async def header_payload_admin(async_client):
    """准备管理员登录token."""
    admin_user = {"username": "admin", "password": "123456"}
    res = await async_client.post("/login", data=admin_user)
    admin_token = res.json()["access_token"]
    yield {"Authorization": f"Bearer {admin_token}"}
