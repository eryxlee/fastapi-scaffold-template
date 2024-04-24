# -*- coding: utf-8 -*-

import pkgutil
from importlib import import_module
from fastapi import APIRouter

api_router = APIRouter()


# 导入所有的子模块
for module in pkgutil.iter_modules(['app/apis']):
    if not module.ispkg:
        continue

    sub_api = import_module(f'app.apis.{module.name}')
    api_router.include_router(sub_api.router, prefix=f"/{module.name}", tags=[module.name])

@api_router.get("/")
async def hello():
    return {"message": "Hello, FastAPI!"}