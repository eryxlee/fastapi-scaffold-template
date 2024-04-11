# -*- coding: utf-8 -*-

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.extensions.fastapi.api import ApiResponse

logger = logging.getLogger(__name__)


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


bad_request_exception_respone = ApiResponse(status=False, code=10001, message="错误的请求", status_code=400)
unauthorized_exception_respone = ApiResponse(status=False, code=10002, message="未经授权的请求", status_code=401)
forbidden_exception_respone = ApiResponse(status=False, code=10003, message="无权访问或数据未授权", status_code=403)
notfound_exception_respone = ApiResponse(status=False, code=10004, message="访问地址不存在", status_code=404)
method_notallowed_exception_respone = ApiResponse(status=False, code=10005, message="不允许使用此方法提交访问", status_code=405)
rate_limit_exception_respone = ApiResponse(status=False, code=10006, message="访问的速度过快", status_code=429)
unknown_error_exception_respone = ApiResponse(status=False, code=10088, message="服务器发生未知错误")


class GlobalExceptionHandler:

    def __init__(self, app: FastAPI):
        self.app = app

    @staticmethod
    async def handle_request_validation_error(
        request: Request, validation_error: RequestValidationError):
        errors = list()

        for error in validation_error.raw_errors:
            for raw_error in error.exc.raw_errors:
                field_error = {
                    'type': 'validation_error',
                    'error': raw_error._loc,
                    'message': str(raw_error.exc)
                }
                errors.append(field_error)

        return ApiResponse(status=False, code=10009, message="数据校验错误", content=errors)

    @staticmethod
    async def handle_api_exception(request: Request, error: APIException):
        return ApiResponse(status=False, code=error.code, message=error.message)

    @staticmethod
    async def handle_exception(request: Request, error: Exception):
        logger.error(f'{request.url} {error}')
        return unknown_error_exception_respone

    def init(self):
        self.app.add_exception_handler(
            RequestValidationError, self.handle_request_validation_error
        )
        self.app.add_exception_handler(APIException, self.handle_api_exception)
        self.app.add_exception_handler(Exception, self.handle_exception)
