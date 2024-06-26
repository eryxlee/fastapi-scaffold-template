# -*- coding: utf-8 -*-

from enum import Enum, IntEnum


class DeleteStatus(IntEnum):
    """删除状态."""

    NOT_SET = 0
    DELETED = 1


class UserGender(IntEnum):
    """用户性别."""

    NOT_SET = 0
    MEN = 1
    WOMEN = 2


class UserAvailableStatus(IntEnum):
    """用户可用状态."""

    NOT_SET = 0
    AVAILABLE = 1
    FORBID = 2


class HttpMethodEnum(str, Enum):
    """HTTP方法."""

    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    CONNECT = "CONNECT"
    TRACE = "TRACE"
