# -*- coding: utf-8 -*-

from fastapi import APIRouter

from ..utils.routeutil import add_all_sub_routers
from .home import base_router

api_router = APIRouter()
# 不加本层的前缀，以免URL太长
add_all_sub_routers(api_router, __name__, __path__, False)

__all__ = ["api_router", "base_router"]
