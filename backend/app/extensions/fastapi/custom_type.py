from pydantic_extra_types.phone_numbers import PhoneNumber


class ChinesePhoneNumber(PhoneNumber):
    """中国电话号码数据类型."""

    default_region_code = "CN"
    phone_format = "E164"
