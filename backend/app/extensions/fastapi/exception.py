# -*- coding: utf-8 -*-

import logging

from typing import Any, List, Optional

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
}


def parse_error(err: Any, field_names: List, raw: bool = True) -> Optional[dict]:
    """
    Parse single error object (such as pydantic-based or fastapi-based) to dict
    :param err: Error object
    :param field_names: List of names of the field that are already processed
    :param raw: Whether this is a raw error or wrapped pydantic error
    :return: dict with name of the field (or "__all__") and actual message
    """
    # if isinstance(err.exc, EnumError):
    #     permitted_values = ", ".join([f"'{val}'" for val in err.exc.enum_values])
    #     message = f"Value is not a valid enumeration member; "f"permitted: {permitted_values}."
    # elif isinstance(err.exc, StrRegexError):
    #     message = "Provided value doesn't match valid format."
    # else:
    message = err["msg"]

    if not raw:
        if len(err["loc"]) == 2:
            if str(err["loc"][0]) in ["body", "query"]:
                name = err["loc"][1]
            else:
                name = err["loc"][0]
        elif len(err["loc"]) == 1:
            if str(err["loc"][0]) == "body":
                name = "__all__"
            else:
                name = str(err["loc"][0])
        else:
            name = "__all__"
    else:
        if len(err["loc"]) == 2:
            name = str(err["loc"][0])
        elif len(err["loc"]) == 1:
            name = str(err["loc"][0])
        else:
            name = "__all__"

    if name in field_names:
        return None

    if message and not any(
            [message.endswith("."), message.endswith("?"), message.endswith("!")]
    ):
        message = message + "."
    message = message.capitalize()

    return {"name": name, "message": message}


def raw_errors_to_fields(raw_errors: List) -> List[dict]:
    """
    Translates list of raw errors (instances) into list of dicts with name/msg
    :param raw_errors: List with instances of raw error
    :return: List of dicts (1 dict for every raw error)
    """
    fields = []
    for top_err in raw_errors:
        # if hasattr(top_err.exc, "raw_errors"):
        #     for err in top_err.exc.raw_errors:
        #         # This is a special case when errors happen both in request
        #         # handling & internal validation
        #         if isinstance(err, list):
        #             err = err[0]
        #         field_err = parse_error(
        #             err,
        #             field_names=list(map(lambda x: x["name"], fields)),
        #             raw=True,
        #         )
        #         if field_err is not None:
        #             fields.append(field_err)
        # else:
            field_err = parse_error(
                top_err,
                field_names=list(map(lambda x: x["name"], fields)),
                raw=False,
            )
            if field_err is not None:
                fields.append(field_err)
    return fields


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
        fields = raw_errors_to_fields(exc.errors())

        return ApiResponse(
            status=False,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="数据校验错误",
            content=fields    # jsonable_encoder({"detail": exc.errors(), "body": exc.body})
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
