# -*- coding: utf-8 -*-

from app.extensions.fastapi.exception import APIException


class UserNotFoundException(APIException):
    code = 10001
    message = "找不到对应的用户"


class UserOrPasswordException(APIException):
    code = 10002
    message = "用户名或密码错误"


class UsernameUsedException(APIException):
    code = 10003
    message = "用户名已经存在"
