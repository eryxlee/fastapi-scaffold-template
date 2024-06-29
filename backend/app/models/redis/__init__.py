# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, AsyncGenerator

import redis.asyncio as redis
from aredis_om import HashModel, get_redis_connection
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from ...config import settings

if TYPE_CHECKING:
    from ...config.app_config import AppConfigSettings


@asynccontextmanager
async def build_redis_cache(
    redis_setting: AppConfigSettings = settings,
) -> AsyncGenerator[redis.Redis[bytes], Any, None]:
    """配置Redis缓存, 并初始化FastAPICache."""
    # 创建redis 连接池链接
    pool = redis.ConnectionPool.from_url(
        redis_setting.REDIS_DSN.unicode_string(),
        encoding="utf8",
        decode_responses=True,
    )
    client = redis.Redis(connection_pool=pool)
    # 初始化FastAPICache
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")

    yield client

    await client.aclose()
    await pool.aclose()


class BaseHashModel(HashModel, abc.ABC):
    """Redis om 基础模型."""

    class Meta:
        """参数定义."""

        global_key_prefix = "test"
        database = get_redis_connection(
            url=settings.REDIS_DSN.unicode_string(),
            decode_responses=True,
        )
