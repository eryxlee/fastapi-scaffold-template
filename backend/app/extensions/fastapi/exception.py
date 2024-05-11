# -*- coding: utf-8 -*-

import logging

from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from app.extensions.fastapi.api import ApiResponse

logger = logging.getLogger(__name__)


error_message = {
    400: "请求参数有误",
    401: "未经授权的请求",
    403: "服务端拒绝提供服务",
    404: "访问地址不存在",
    405: "请求方法不能被用于请求相应的资源",
    500: "服务器发生未知错误",
    10000: "数据校验错误"
}


class APIException(Exception):
    """api 通用异常
    """
    code = 10000
    message = 'A server error occurred.'

    def __init__(self, code=None, message=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message

    def __repr__(self):
        return '<{} {}: {}>'.format(
            self.__class__, self.code, self.message
        )


class GlobalExceptionHandler:

    def __init__(self, app: FastAPI):
        self.app = app

    @staticmethod
    async def handle_request_validation_error(request: Request, exc: RequestValidationError):
        return ApiResponse(
            status=False,
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @staticmethod
    async def handle_api_exception(request: Request, error: APIException):
        return ApiResponse(status=False, code=error.code, message=error.message)

    @staticmethod
    async def handle_http_exception(request: Request, error: HTTPException):
        # 将出错信息转换成中文
        message = error_message[error.status_code] \
            if error_message.get(error.status_code) else error.detail

        return ApiResponse(
            status=False,
            code=error.status_code,
            message=message,
            status_code=error.status_code # 保留status_code，该值不会出现在输出内容中
        )

    @staticmethod
    async def handle_exception(request: Request, error: Exception):
        return ApiResponse(
            status=False,
            code=500, # 未知错误都归结于500
            message=(
                f"在链接 {request.url} 处使用 {request.method} 出错."
                f" 出错信息为 {error!r}."
            ),
            status_code=500
        )

    def init(self):
        self.app.add_exception_handler(
            RequestValidationError, self.handle_request_validation_error
        )
        self.app.add_exception_handler(APIException, self.handle_api_exception)
        self.app.add_exception_handler(HTTPException, self.handle_http_exception)
        self.app.add_exception_handler(Exception, self.handle_exception)
