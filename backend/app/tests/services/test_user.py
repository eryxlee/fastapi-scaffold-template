# -*- coding: utf-8 -*-

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio(scope="session")
async def test_create_user(
    setup_initial_dataset,
    async_session: AsyncSession,
    user_payload,
) -> None:
    from ...services.user import UserService

    user_service = UserService(async_session)

    ouser = await user_service.create(user_payload)
    assert ouser.id != 0
