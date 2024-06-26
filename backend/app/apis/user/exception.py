# -*- coding: utf-8 -*-

from app.extensions.fastapi.exception import APIException


class UserNotFoundException(APIException):
    """找不到对应的用户异常类."""

    status_code = 400
    code = 10001
    message = "找不到对应的用户"


class UserOrPasswordErrorException(APIException):
    """用户名或密码错误异常类."""

    status_code = 400
    code = 10002
    message = "用户名或密码错误"


class UsernameUsedException(APIException):
    """用户名已经存在异常类."""

    status_code = 400
    code = 10003
    message = "用户名已经存在"
