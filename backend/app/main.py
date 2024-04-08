from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.dependencies import get_current_user  # 假设这里定义了依赖项
from app.api import api_router  # 假设这里定义了路由
from app.models import engine, Base  # 假设这是数据库相关配置
# from app.models import User  # 假设这是你的用户模型

# 创建 FastAPI 应用实例
app = FastAPI(
    title="My FastAPI App",
    version="0.1.0",
    description="This is a very fancy app made with FastAPI",
)

# # 添加 CORS 中间件
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 假设我们有一个全局的数据库会话
# Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

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
app.include_router(api_router)
app

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
