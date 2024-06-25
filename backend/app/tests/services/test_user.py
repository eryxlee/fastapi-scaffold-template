# -*- coding: utf-8 -*-

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user import UserCreate
from ...services.user import UserService


@pytest.mark.asyncio(scope="session")
async def test_create_user(
    async_session: AsyncSession, user_to_create: UserCreate, dataset
) -> None:
    user_service = UserService(async_session)

    ouser = await user_service.create(user_to_create)
    assert ouser.id != 0
