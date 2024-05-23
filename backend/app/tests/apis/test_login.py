# -*- coding: utf-8 -*-

import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import *
from app.tests.datas.user_data import user_to_create, dataset


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_non_existing_username(
    async_client: AsyncClient
):
    fake_user = {
        "username": "non-existing-username",
        "password": "fake-password"
    }
    res = await async_client.post('/login', data=fake_user)
    assert res.status_code == 400
    print(res.json())


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_wrong_password(
    async_client: AsyncClient,
    user_to_create,
    dataset,
    api_prefix
):
    # Create the user
    res = await async_client.post(f'{api_prefix}/user/signup', json=user_to_create.model_dump())
    assert res.json()["data"]['name'] == user_to_create.name
    user_id = res.json()['data']["id"]

    # Try to login with wrong password
    fake_user = {
        "username": "test",
        "password": "fake-password"
    }
    res = await async_client.post('/login', data=fake_user)
    assert res.status_code == 400
    assert res.json()['message'] == '用户名或密码错误'

    res = await async_client.delete(f'{api_prefix}/user/{user_id}')


@pytest.mark.asyncio(scope="session")
async def test_user_login_with_success(
    async_client: AsyncClient,
    user_to_create,
    dataset,
    api_prefix
):
    # Create the user
    res = await async_client.post(f'{api_prefix}/user/signup', json=user_to_create.model_dump())
    assert res.json()["data"]['name'] == user_to_create.name
    user_id = res.json()['data']["id"]

    # Try to login with wrong password
    valid_user = {
        "username": "test",
        "password": "123456"
    }
    res = await async_client.post('/login', data=valid_user)
    assert res.status_code == 200
    assert res.json()['access_token']

    res = await async_client.delete(f'{api_prefix}/user/{user_id}')

