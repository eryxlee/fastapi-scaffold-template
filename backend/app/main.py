# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .apis import api_router, base_router
from .config import settings
from .extensions.fastapi.exception import register_global_exception
from .extensions.fastapi.middleware import MetaDataAdderMiddleware, TimingMiddleware
from .models import init_db
from .models.redis import build_redis_cache


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: ANN201
    """自定义Fastapi生命周期."""
    # 创建数据库表(如果尚未创建)
    await init_db()

    async with build_redis_cache(settings) as client:
        app.state.redis = client
        yield


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
