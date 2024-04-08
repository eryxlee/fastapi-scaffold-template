# -*- coding: utf-8 -*-

from fastapi import APIRouter

from app.api.todo.views import router as todo_router
from app.api.user.views import router as user_router

api_router = APIRouter()


# api_router.include_router(login.router, tags=["login"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(todo_router, prefix="/todo", tags=["todo"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])

@api_router.get("/")
async def hello():
    return {"message": "Hello, FastAPI!"}