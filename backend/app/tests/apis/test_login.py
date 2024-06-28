# -*- coding: utf-8 -*-

from typing import Any

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)

from ...models.user import UserCreate
from ..datas.user_data import dataset, user_to_create  # noqa: F401


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_non_existing_username(async_client: AsyncClient) -> None:
    fake_user = {"username": "non-existing-username", "password": "fake-password"}
    res = await async_client.post("/login", data=fake_user)
    assert res.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_wrong_password(
    async_client: AsyncClient,
    user_to_create: UserCreate,  # noqa: F811
    dataset: Any,  # noqa: F811
    api_prefix: str,
) -> None:
    # Create the user
    res = await async_client.post(f"{api_prefix}/user/signup", json=user_to_create.model_dump())
    assert res.json()["data"]["name"] == user_to_create.name
    user_id = res.json()["data"]["id"]

    # Try to login with wrong password
    fake_user = {"username": "test", "password": "fake-password"}
    res = await async_client.post("/login", data=fake_user)
    assert res.status_code == HTTP_400_BAD_REQUEST
    assert res.json()["message"] == "用户名或密码错误"

    res = await async_client.delete(f"{api_prefix}/user/{user_id}")


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_success(
    async_client: AsyncClient,
    user_to_create: UserCreate,  # noqa: F811
    dataset: Any,  # noqa: F811
    api_prefix: str,
) -> None:
    # Create the user
    res = await async_client.post(f"{api_prefix}/user/signup", json=user_to_create.model_dump())
    assert res.json()["data"]["name"] == user_to_create.name
    user_id = res.json()["data"]["id"]

    # Try to login with wrong password
    valid_user = {"username": "test", "password": "123456"}
    res = await async_client.post("/login", data=valid_user)
    assert res.status_code == HTTP_200_OK
    assert res.json()["access_token"]

    res = await async_client.delete(f"{api_prefix}/user/{user_id}")
