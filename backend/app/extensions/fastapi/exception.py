# -*- coding: utf-8 -*-

import logging
from typing import Any, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from .api import ApiResponse

logger = logging.getLogger(__name__)


CUSTOM_VALIDATION_ERROR_MESSAGES = {
    "arguments_type": "参数类型输入错误",
    "assertion_error": "断言执行错误",
    "bool_parsing": "布尔值输入解析错误",
    "bool_type": "布尔值类型输入错误",
    "bytes_too_long": "字节长度输入过长",
    "bytes_too_short": "字节长度输入过短",
    "bytes_type": "字节类型输入错误",
    "callable_type": "可调用对象类型输入错误",
    "dataclass_exact_type": "数据类实例类型输入错误",
    "dataclass_type": "数据类类型输入错误",
    "date_from_datetime_inexact": "日期分量输入非零",
    "date_from_datetime_parsing": "日期输入解析错误",
    "date_future": "日期输入非将来时",
    "date_parsing": "日期输入验证错误",
    "date_past": "日期输入非过去时",
    "date_type": "日期类型输入错误",
    "datetime_future": "日期时间输入非将来时间",
    "datetime_object_invalid": "日期时间输入对象无效",
    "datetime_parsing": "日期时间输入解析错误",
    "datetime_past": "日期时间输入非过去时间",
    "datetime_type": "日期时间类型输入错误",
    "decimal_max_digits": "小数位数输入过多",
    "decimal_max_places": "小数位数输入错误",
    "decimal_parsing": "小数输入解析错误",
    "decimal_type": "小数类型输入错误",
    "decimal_whole_digits": "小数位数输入错误",
    "dict_type": "字典类型输入错误",
    "enum": "枚举成员输入错误，允许：{expected}",
    "extra_forbidden": "禁止额外字段输入",
    "finite_number": "有限值输入错误",
    "float_parsing": "浮点数输入解析错误",
    "float_type": "浮点数类型输入错误",
    "frozen_field": "冻结字段输入错误",
    "frozen_instance": "冻结实例禁止修改",
    "frozen_set_type": "冻结类型禁止输入",
    "get_attribute_error": "获取属性错误",
    "greater_than": "输入值过大",
    "greater_than_equal": "输入值过大或相等",
    "int_from_float": "整数类型输入错误",
    "int_parsing": "整数输入解析错误",
    "int_parsing_size": "整数输入解析长度错误",
    "int_type": "整数类型输入错误",
    "invalid_key": "输入无效键值",
    "is_instance_of": "类型实例输入错误",
    "is_subclass_of": "类型子类输入错误",
    "iterable_type": "可迭代类型输入错误",
    "iteration_error": "迭代值输入错误",
    "json_invalid": "JSON 字符串输入错误",
    "json_type": "JSON 类型输入错误",
    "less_than": "输入值过小",
    "less_than_equal": "输入值过小或相等",
    "list_type": "列表类型输入错误",
    "literal_error": "字面值输入错误",
    "mapping_type": "映射类型输入错误",
    "missing": "缺少必填字段",
    "missing_argument": "缺少参数",
    "missing_keyword_only_argument": "缺少关键字参数",
    "missing_positional_only_argument": "缺少位置参数",
    "model_attributes_type": "模型属性类型输入错误",
    "model_type": "模型实例输入错误",
    "multiple_argument_values": "参数值输入过多",
    "multiple_of": "输入值非倍数",
    "no_such_attribute": "分配无效属性值",
    "none_required": "输入值必须为 None",
    "recursion_loop": "输入循环赋值",
    "set_type": "集合类型输入错误",
    "string_pattern_mismatch": "字符串约束模式输入不匹配",
    "string_sub_type": "字符串子类型（非严格实例）输入错误",
    "string_too_long": "字符串输入过长",
    "string_too_short": "字符串输入过短",
    "string_type": "字符串类型输入错误",
    "string_unicode": "字符串输入非 Unicode",
    "time_delta_parsing": "时间差输入解析错误",
    "time_delta_type": "时间差类型输入错误",
    "time_parsing": "时间输入解析错误",
    "time_type": "时间类型输入错误",
    "timezone_aware": "缺少时区输入信息",
    "timezone_naive": "禁止时区输入信息",
    "too_long": "输入过长",
    "too_short": "输入过短",
    "tuple_type": "元组类型输入错误",
    "unexpected_keyword_argument": "输入意外关键字参数",
    "unexpected_positional_argument": "输入意外位置参数",
    "union_tag_invalid": "联合类型字面值输入错误",
    "union_tag_not_found": "联合类型参数输入未找到",
    "url_parsing": "URL 输入解析错误",
    "url_scheme": "URL 输入方案错误",
    "url_syntax_violation": "URL 输入语法错误",
    "url_too_long": "URL 输入过长",
    "url_type": "URL 类型输入错误",
    "uuid_parsing": "UUID 输入解析错误",
    "uuid_type": "UUID 类型输入错误",
    "uuid_version": "UUID 版本类型输入错误",
    "value_error": "值输入错误",
}


error_message = {
    400: "请求参数有误",
    401: "未经授权的请求",
    403: "服务端拒绝提供服务",
    404: "访问地址不存在",
    405: "请求方法不能被用于请求相应的资源",
    500: "服务器发生未知错误",
}


def parse_error(err: Any, field_names: List, raw: bool = True) -> Optional[dict]:
    """Parse single error object (such as pydantic-based or fastapi-based) to dict.

    :param err: Error object
    :param field_names: List of names of the field that are already processed
    :param raw: Whether this is a raw error or wrapped pydantic error
    :return: dict with name of the field (or "__all__") and actual message
    """
    # if isinstance(err.exc, EnumError):
    #     permitted_values = ", ".join([f"'{val}'" for val in err.exc.enum_values])
    #     message = f"Value is not a valid enumeration member; "f"permitted: {permitted_values}."
    # else:

    message = CUSTOM_VALIDATION_ERROR_MESSAGES.get(err["type"])
    if message:
        ctx = err.get("ctx")
        message = message.format(**ctx) if ctx else message
    else:
        message = err["msg"]

    if not raw:
        if len(err["loc"]) == 2:
            if str(err["loc"][0]) in ["body", "query"]:
                name = str(err["loc"][1])
            else:
                name = str(err["loc"][0])
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

    if message and not any([message.endswith("."), message.endswith("?"), message.endswith("!")]):
        message = message + "."
    message = message.capitalize()

    return {"name": name, "message": message}


def raw_errors_to_fields(raw_errors: List) -> List[dict]:
    """Translates list of raw errors (instances) into list of dicts with name/msg.

    :param raw_errors: List with instances of raw error
    :return: List of dicts (1 dict for every raw error)
    """
    fields = []
    for top_err in raw_errors:
        if hasattr(top_err, "exc") and hasattr(top_err.exc, "raw_errors"):
            for err in top_err.exc.raw_errors:
                # This is a special case when errors happen both in request
                # handling & internal validation
                if isinstance(err, list):
                    err = err[0]
                field_err = parse_error(
                    err,
                    field_names=list(map(lambda x: x["name"], fields)),
                    raw=True,
                )
                if field_err is not None:
                    fields.append(field_err)
        else:
            field_err = parse_error(
                top_err,
                field_names=list(map(lambda x: x["name"], fields)),
                raw=False,
            )
            if field_err is not None:
                fields.append(field_err)
    return fields


def handle_validation_exception(exc: RequestValidationError | ValidationError):
    """数据验证异常处理.

    :param exc:
    :return:
    """
    errors = raw_errors_to_fields(exc.errors())
    message = "请求参数非法"
    try:
        error = exc.errors()[0]
        if error.get("type") == "json_invalid":
            message = "json解析失败"
    except Exception:
        message = "json解析失败"

    return ApiResponse(
        status=False,
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=message,
        content=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


class APIException(Exception):  # noqa: N818
    """Api 通用异常."""

    status_code = 200
    code = 10000
    message = "A server error occurred."

    def __init__(self, status_code=None, code=None, message=None):
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message

    def __repr__(self):
        return f"<{self.__class__} {self.status_code} {self.code}: {self.message}>"


# class GlobalExceptionHandler:
def register_global_exception(app: FastAPI):
    """注册全局异常处理处理逻辑."""

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """Fastapi 数据验证异常处理.

        :param request:
        :param exc:
        :return:
        """
        return handle_validation_exception(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Pydantic 数据验证异常处理.

        :param request:
        :param exc:
        :return:
        """
        return await handle_validation_exception(exc)

    @app.exception_handler(APIException)
    async def handle_api_exception(request: Request, exc: APIException):
        """自定义API异常处理.

        :param request:
        :param exc:
        :return:
        """
        return ApiResponse(
            status=False,
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """全局HTTP异常处理.

        :param request:
        :param exc:
        :return:
        """
        # 将出错信息转换成中文
        message = (
            error_message[exc.status_code] if error_message.get(exc.status_code) else exc.detail
        )

        return ApiResponse(
            status=False,
            code=exc.status_code,
            message=message,
            status_code=exc.status_code,  # 保留status_code，该值不会出现在输出内容中
            headers=exc.headers,  # 保留headers，该值不会出现在输出内容中
        )

    @app.exception_handler(Exception)
    async def handle_exception(request: Request, exc: Exception):
        """未知异常处理.

        :param request:
        :param exc:
        :return:
        """
        return ApiResponse(
            status=False,
            code=500,  # 未知错误都归结于500
            message=(f"在链接 {request.url} 处使用 {request.method} 出错." f" 出错信息为 {exc!r}."),
            status_code=500,
        )


_all__ = ["APIException", "register_global_exception"]
