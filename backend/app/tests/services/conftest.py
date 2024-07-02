# -*- coding: utf-8 -*-

import pytest_asyncio


@pytest_asyncio.fixture(scope="function")
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
