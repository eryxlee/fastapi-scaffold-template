# -*- coding: utf-8 -*-

import abc

from aredis_om import HashModel, get_redis_connection

from ...config import settings


class BaseHashModel(HashModel, abc.ABC):
    class Meta:
        global_key_prefix = "test"
        database = get_redis_connection(
            url=settings.REDIS_DSN.unicode_string(), decode_responses=True
        )
