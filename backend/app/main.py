# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.models import engine, Base
from app.config import settings

from app.extensions.fastapi.middleware import TimingMiddleware, MetaDataAdderMiddleware
from app.extensions.fastapi.exception import GlobalExceptionHandler


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
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

# 应用启动事件监听器
@app.on_event("startup")
async def startup_event():
    # 创建数据库表（如果尚未创建）
    Base.metadata.create_all(bind=engine)
    # 你可以在这里执行其他需要在应用启动时执行的代码

# # 应用关闭事件监听器
# @app.on_event("shutdown")
# async def shutdown_event():
#     # 你可以在这里执行需要在应用关闭时执行的代码，比如关闭数据库连接等
#     pass

# 将路由添加到应用中
app.include_router(api_router, prefix=settings.API_PREFIX)
