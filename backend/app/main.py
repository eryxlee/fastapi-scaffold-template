# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from .apis import api_router, base_router
from .config import settings
from .extensions.fastapi.exception import register_global_exception
from .extensions.fastapi.middleware import MetaDataAdderMiddleware, TimingMiddleware


@asynccontextmanager
async def lifespan(application: FastAPI):
    # 创建数据库表（如果尚未创建）
    from app.models import init_db

    await init_db()
    # 创建redis链接，并赋值给app.state
    pool = redis.ConnectionPool.from_url(
        settings.REDIS_DSN.unicode_string(), encoding="utf8", decode_responses=True
    )
    client = redis.Redis(connection_pool=pool)
    app.state.redis = client
    # 初始化FastAPICache
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")

    yield

    await client.aclose()
    await pool.aclose()


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan,
)

# 添加api运行计时中间件
app.add_middleware(TimingMiddleware)
# 添加元数据中间件（统一API输出结构）
app.add_middleware(MetaDataAdderMiddleware)
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 统一异常输出结构
register_global_exception(app)
# 设置静态文件目录
# app.mount("/static", StaticFiles(directory="static"), name="static")
# 将路由添加到应用中
app.include_router(base_router)
app.include_router(api_router, prefix=settings.API_PREFIX)
