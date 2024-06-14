# -*- coding: utf-8 -*-

import hashlib

from typing import Callable, Optional
from starlette.requests import Request
from starlette.responses import Response


def noself_key_builder(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    from fastapi_cache import FastAPICache

    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    ordered_kwargs = sorted(kwargs.items())
    noself_args = args[1:] if args else args
    cache_key = (
        prefix
        + hashlib.md5(  # nosec:B303
            f"{func.__module__}:{func.__name__}:{noself_args}:{ordered_kwargs}".encode()
        ).hexdigest()
    )
    return cache_key
