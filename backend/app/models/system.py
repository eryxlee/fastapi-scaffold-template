# -*- coding: utf-8 -*-

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    SmallInteger,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, CommonMixin, idPk

class SysLog(Base):
    """ 日志表 """

    id: Mapped[idPk]
    url: Mapped[str] = mapped_column(String(64), comment="请求url")
    method: Mapped[str] = mapped_column(String(10), comment="请求方法")
    ip: Mapped[str] = mapped_column(String(20), comment="请求ip")
    params: Mapped[str | None] = mapped_column(String(255), comment="请求参数")
    spend_time: Mapped[str | None] = mapped_column(String(30), comment="响应时间")
    create_time: Mapped[str | None] = mapped_column(String(30), comment="创建时间")