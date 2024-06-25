# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import BaseModel


class CommonSchemaMixin(BaseModel):
    id: int
    create_time: datetime | None
    update_time: datetime | None

    class Config:
        # from_attributes 将告诉 Pydantic 模型读取数据，即它不是一个 dict，而是一个 ORM 模型
        # https://docs.pydantic.dev/2.0/usage/models/#arbitrary-class-instances
        from_attributes = True
        # 自定义编码器
        json_encoders = {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
