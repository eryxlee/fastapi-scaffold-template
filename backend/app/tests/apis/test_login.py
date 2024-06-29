# -*- coding: utf-8 -*-

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_non_existing_username(async_client: AsyncClient) -> None:
    fake_user = {"username": "non-existing-username", "password": "fake-password"}
    res = await async_client.post("/login", data=fake_user)
    assert res.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_wrong_password(
    setup_initial_dataset,
    async_client: AsyncClient,
    user_payload,
    api_prefix,
) -> None:
    # Create the user
    res = await async_client.post(f"{api_prefix}/user/signup", json=user_payload.model_dump())
    assert res.json()["data"]["name"] == user_payload.name
    user_id = res.json()["data"]["id"]

    # Try to login with wrong password
    fake_user = {"username": "test", "password": "fake-password"}
    res = await async_client.post("/login", data=fake_user)
    assert res.status_code == HTTP_400_BAD_REQUEST
    assert res.json()["message"] == "用户名或密码错误"

    res = await async_client.delete(f"{api_prefix}/user/{user_id}")


@pytest.mark.asyncio(scope="session")
async def test_user_login_successful(
    setup_initial_dataset,
    async_client: AsyncClient,
    user_payload,
    api_prefix,
) -> None:
    # Create the user
    res = await async_client.post(f"{api_prefix}/user/signup", json=user_payload.model_dump())
    assert res.json()["data"]["name"] == user_payload.name
    user_id = res.json()["data"]["id"]

    # Try to login with wrong password
    valid_user = {"username": "test", "password": "123456"}
    res = await async_client.post("/login", data=valid_user)
    assert res.status_code == HTTP_200_OK
    assert res.json()["access_token"]

    res = await async_client.delete(f"{api_prefix}/user/{user_id}")
