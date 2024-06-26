# -*- coding: utf-8 -*-

import datetime
import decimal
import json


class CustomJsonEncoder(json.JSONEncoder):
    """自定义JSON格式化."""

    def default(self, obj):  # noqa: D102
        if hasattr(obj, "keys") and hasattr(obj, "__getitem__"):
            return dict(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        return json.JSONEncoder.default(self, obj)
