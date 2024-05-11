# -*- coding: utf-8 -*-

from sqlalchemy import (
    String,
    SmallInteger,
    text
)

from passlib.hash import pbkdf2_sha256

from pydantic import EmailStr
from sqlmodel import Session, Field, SQLModel
from . import TimestampModel, IDModel, TableBase, CommonPropertyModel


class UserBase(SQLModel):
    """ 用户模型公共部分 """
    name: str = Field(default="", max_length=60, nullable=False, description="用户名", sa_type=String(60))
    avatar: str | None = Field(max_length=128, nullable=True, description="头像", sa_type=String(128))
    email: EmailStr | None = Field(max_length=128, nullable=True, description="邮件", sa_type=String(128))
    gender: int | None = Field(nullable=True, description="性别", sa_type=SmallInteger)
    phone: str | None = Field(max_length=36, nullable=True, description="电话", sa_type=String(36))


class UserCreate(UserBase):
    """ 注册时采用的用户模型 """
    password: str = Field(default="", max_length=128, nullable=False, description="密码", sa_type=String(128))


class UserUpdate(UserCreate):
    """ 更新时采用的用户模型 """
    pass


class User(
    TimestampModel,
    CommonPropertyModel,
    UserCreate,
    IDModel,
    TableBase,
    table = True):
    """ 展示用户详情信息的用户模型 """
    is_active: int = Field(default=0, nullable=True, description="是否激活", sa_type=SmallInteger)

    def verify_password(self, raw_password) -> bool:
        # 使用passlib验证密码
        return pbkdf2_sha256.verify(raw_password, self.password)

    @classmethod
    def encrypt_password(self, raw_password) -> str:
        return pbkdf2_sha256.hash(raw_password)








# class User(Base, CommonMixin):

#     id: Mapped[idPk]
#     name: Mapped[str] = mapped_column(String(60), unique=True, comment="用户名")
#     password: Mapped[str] = mapped_column(String(128), comment="密码")
#     avatar: Mapped[str | None] = mapped_column(String(127), comment="头像")
#     email: Mapped[str | None] = mapped_column(String(60), comment="邮件地址")
#     gender: Mapped[int | None] = mapped_column(SmallInteger, server_default=text('0'), comment="性别: 0 未知 1 男 2 女")
#     phone: Mapped[str | None] = mapped_column(String(30), comment="手机号")
#     is_active: Mapped[int | None] = mapped_column(SmallInteger, server_default=text('0'), comment="可用：0 可用，1 禁用")

#     user_role = relationship("UserRole", back_populates="user")

#     # 用户与TODO的关联关系可以在这里定义
#     # todos = relationship("Todo", back_populates="owner")

#     def verify_password(self, raw_password) -> bool:
#         # 使用passlib验证密码
#         return pbkdf2_sha256.verify(raw_password, self.password)

#     def set_encrypt_password(self, raw_password) -> None:
#         self.password = pbkdf2_sha256.hash(raw_password)


# class Role(Base, CommonMixin):
#     """ 角色表 """

#     id: Mapped[idPk]
#     name: Mapped[str] = mapped_column(String(32), comment="角色名称")
#     code: Mapped[str] = mapped_column(String(32), comment="角色code")
#     description: Mapped[str | None] = mapped_column(String(60), comment="角色描述")

#     user_role = relationship("UserRole", back_populates="role")
#     role_resource = relationship("RoleResource", back_populates="role")


# class UserRole(Base):
#     """ 用户角色表 """

#     id: Mapped[idPk]
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), comment="用户id")
#     role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), comment="角色id")

#     user = relationship("User", back_populates="user_role")
#     role = relationship("Role", back_populates="user_role")


# class Resource(Base, CommonMixin):
#     """ 资源表 """

#     id: Mapped[idPk]
#     name: Mapped[str] = mapped_column(String(32), comment="资源名称")
#     level: Mapped[int] = mapped_column(SmallInteger, server_default=text('0'), comment="层级: 0 目录 1 菜单 2 权限")
#     pid: Mapped[int] = mapped_column(server_default=text('0'), comment="父节点id")
#     icon: Mapped[str | None] = mapped_column(String(64), comment="图标")
#     menu_url: Mapped[str | None] = mapped_column(String(64), comment="页面路由")
#     request_url: Mapped[str | None] = mapped_column(String(64), comment="请求url")
#     permission_code: Mapped[str | None] = mapped_column(String(32), comment="权限code")

#     role_resource = relationship("RoleResource", back_populates="resource")


# class RoleResource(Base):
#     """ 角色资源表 """

#     id: Mapped[idPk]
#     role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), comment="角色id")
#     resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), comment="资源id")

#     role = relationship("Role", back_populates="role_resource")
#     resource = relationship("Resource", back_populates="role_resource")
