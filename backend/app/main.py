# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.apis import api_router, base_router

from app.extensions.fastapi.middleware import TimingMiddleware, MetaDataAdderMiddleware
from app.extensions.fastapi.exception import GlobalExceptionHandler


# 应用启动事件监听器
async def startup_hook():
    # 创建数据库表（如果尚未创建）
    from app.models import init_db
    await init_db()
    # 你可以在这里执行其他需要在应用启动时执行的代码


# # 应用关闭事件监听器
async def shutdown_hook():
    # 你可以在这里执行需要在应用关闭时执行的代码，比如关闭数据库连接等
    pass


@asynccontextmanager
async def lifespan(application: FastAPI):
    await startup_hook()
    yield
    await shutdown_hook()


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
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
GlobalExceptionHandler(app).init()
# 设置静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
# 将路由添加到应用中
app.include_router(base_router)
app.include_router(api_router, prefix=settings.API_PREFIX)
