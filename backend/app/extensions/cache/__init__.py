# -*- coding: utf-8 -*-

import hashlib
from typing import Callable, Optional

from fastapi_cache import FastAPICache
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
    """使用在类函数上的cache key builder.

    本key builder在计算key的时候忽略self, 以免每次self不同导致key不同
    """
    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    ordered_kwargs = sorted(kwargs.items())
    noself_args = args[1:] if args else args
    cache_key = (
        prefix
        + hashlib.sha256(  # nosec:B303
            f"{func.__module__}:{func.__name__}:{noself_args}:{ordered_kwargs}".encode()
        ).hexdigest()
    )
    return cache_key


def request_key_builder(
    func: Callable,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
) -> str:
    """API route上使用的key builder.

    本key builder在计算key的时候使用Url参数与header参数, 没有采用body. 缓存建议使用在GET请求中,
    有body的请求一般都是POST类请求, 不建议加缓存
    """
    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    query_params = repr(sorted(request.query_params.items()))
    header_params = repr(sorted(request.headers.items()))
    cache_key = (
        prefix
        + hashlib.sha256(
            f"{request.method.lower()}:{request.url.path}:{query_params}:{header_params}".encode()
        ).hexdigest()
    )

    return cache_key
