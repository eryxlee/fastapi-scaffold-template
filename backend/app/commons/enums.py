# -*- coding: utf-8 -*-

from enum import Enum, IntEnum


class DeleteStatus(IntEnum):
    """删除状态"""
    NOT_SET = 0
    DELETED = 1


class UserGender(IntEnum):
    """用户性别"""
    NOT_SET = 0
    MEN = 1
    WOMEN = 2


class UserAvailableStatus(IntEnum):
    """用户可用状态"""
    NOT_SET = 0
    AVAILABLE = 1
    FORBID = 2
