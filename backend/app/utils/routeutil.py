# -*- coding: utf-8 -*-

import pkgutil
from importlib import import_module

from fastapi import APIRouter


def add_all_sub_routers(router: APIRouter, name: str, path: str, prefix: bool) -> any:
    """查找模块下所有子模块, 将其拥有的router加入到上级router中."""
    # 查找所有子模块，形成 (模块名，子模块) 数据元组
    modules = [
        (module_info.name, import_module(f"{name}.{module_info.name}"))
        for module_info in pkgutil.iter_modules(path)
    ]

    # 添加到router中
    for name, mod in modules:
        if getattr(mod, "router", None):
            if prefix:
                router.include_router(mod.router, prefix=f"/{name}")
            else:
                router.include_router(mod.router)
