# -*- coding: utf-8 -*-

from fastapi import APIRouter

from app.utils.routeutil import add_all_sub_routers
import app.apis as api_module

api_router = APIRouter()
# 不加本层的前缀，以免URL太长
add_all_sub_routers(api_router, api_module, False)

from app.apis.home import base_router

__all__ = ["api_router", "base_router"]
