# -*- coding: utf-8 -*-

import json
import typing

from fastapi.responses import JSONResponse

from ..serializer.json import CustomJsonEncoder


class ApiResponse(JSONResponse):
    """请求统一返回结构体."""

    def __init__(
        self,
        status: bool = True,
        code: int = 0,
        message: str = "成功",
        content: typing.Any = None,
        **options,
    ):
        """初始化函数."""
        self.status = status
        self.code = code
        self.message = message

        # 返回内容体
        body = dict(status=self.status, code=self.code, message=self.message, data=content)
        super().__init__(content=body, **options)

    def render(self, content: typing.Any) -> bytes:
        """渲染函数."""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJsonEncoder,
        ).encode("utf-8")
