# -*- coding: utf-8 -*-

from fastapi import APIRouter

from ...utils.routeutil import add_all_sub_routers

router = APIRouter(tags=["user"])

add_all_sub_routers(router, __name__, __path__, True)

__ALL__ = ["router"]
