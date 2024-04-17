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


class User(Base, CommonMixin):

    id: Mapped[idPk]
    name: Mapped[str] = mapped_column(String(60), unique=True, comment="用户名")
    password: Mapped[str] = mapped_column(String(64), comment="密码")
    avatar: Mapped[str | None] = mapped_column(String(127), comment="头像")
    email: Mapped[str | None] = mapped_column(String(60), comment="邮件地址")
    gender: Mapped[int | None] = mapped_column(SmallInteger, server_default=text('0'), comment="性别: 0 未知 1 男 2 女")
    phone: Mapped[str | None] = mapped_column(String(30), comment="手机号")
    is_active: Mapped[int | None] = mapped_column(SmallInteger, server_default=text('0'), comment="可用：0 可用，1 禁用")

    # user_role = relationship("UserRole", back_populates="user")

    # 用户与TODO的关联关系可以在这里定义
    # todos = relationship("Todo", back_populates="owner")

    # def verify_password(self, raw_password):
    #     # 使用passlib验证密码
    #     return verify_password(raw_password, self.hashed_password)
