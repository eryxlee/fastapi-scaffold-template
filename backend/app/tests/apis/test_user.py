# -*- coding: utf-8 -*-
import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
)


@pytest.mark.asyncio()
async def test_read_users_by_admin(
    setup_initial_dataset,
    setup_redis_cache,
    async_client: AsyncClient,
    api_prefix: str,
    header_payload_admin: str,
):
    response = await async_client.get(
        f"{api_prefix}/user/",
        headers=header_payload_admin,
        params={"page": 1, "page_size": 10},
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["status"] is True
    assert data["data"]["page"]["page"] == 1
    assert data["data"]["page"]["total"] == 3  # noqa: PLR2004


@pytest.mark.asyncio()
async def test_user_signup(
    setup_initial_dataset,
    async_client: AsyncClient,
    user_payload,
    api_prefix: str,
    header_payload_admin: str,
):
    response = await async_client.post(
        f"{api_prefix}/user/signup",
        json=user_payload.model_dump(),
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["data"]["name"] == user_payload.name


@pytest.mark.asyncio()
async def test_user_signup_twice(
    setup_initial_dataset,
    async_client: AsyncClient,
    user_payload,
    api_prefix: str,
):
    await async_client.post(f"{api_prefix}/user/signup", json=user_payload.model_dump())
    res = await async_client.post(f"{api_prefix}/user/signup", json=user_payload.model_dump())
    data = res.json()
    assert data["status"] is False


@pytest.mark.asyncio()
async def test_user_create_wrong_email_format(
    setup_initial_dataset,
    async_client: AsyncClient,
    api_prefix: str,
):
    from ...models.user import UserCreate

    wrong_user = UserCreate(
        email="wrong.user@gmail.com",
        name="wrong_user",
        password="wrong_user_password",
    )

    wrong_user.email = "wrong_email"
    res = await async_client.post(f"{api_prefix}/user/signup", json=wrong_user.model_dump())
    data = res.json()
    assert data["status"] is False


@pytest.mark.asyncio()
async def test_user_create_wrong_password_format(
    setup_initial_dataset,
    async_client: AsyncClient,
    api_prefix: str,
):
    from ...models.user import UserCreate

    wrong_user = UserCreate(
        email="wrong.user@gmail.com",
        name="wrong_user",
        password="wrong_user_password",
    )

    wrong_user.password = "13"
    res = await async_client.post(f"{api_prefix}/user/signup", json=wrong_user.model_dump())
    data = res.json()
    assert data["status"] is False
