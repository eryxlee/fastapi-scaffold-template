# -*- coding: utf-8 -*-

from fastapi import APIRouter

from app.utils.routeutil import add_all_sub_routers
import app.apis.user as user_module

router = APIRouter(tags=["user"])

add_all_sub_routers(router, user_module, True)

__ALL__ = ["router"]
