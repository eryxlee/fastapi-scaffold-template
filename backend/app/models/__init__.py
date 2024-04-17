# -*- coding: utf-8 -*-

import re
from datetime import datetime
from typing_extensions import Annotated

from sqlalchemy import String, Integer, SmallInteger, func, text
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    sessionmaker,
    declared_attr,
    mapped_column,
    Mapped
)
from sqlalchemy import create_engine

from app.config import settings


engine = create_engine(str(settings.MARIADB_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
idPk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, comment="主键ID")]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    """ ORM 基类"""
    __table_args__ = {
        "mysql_engine": "InnoDB",  # MySQL引擎
        "mysql_charset": "utf8mb4",  # 设置表的字符集
        "mysql_collate": "utf8mb4_general_ci",  # 设置表的校对集
    }

    # 类名转表名
    # https://blog.csdn.net/mouday/article/details/90079956
    @declared_attr.directive
    def __tablename__(cls) -> str:
        snake_case = re.sub(r"(?P<key>[A-Z])", r"_\g<key>", cls.__name__)
        return snake_case.lower().strip('_')

    # json 输出
    def to_json(self):
        if hasattr(self, '__table__'):
            return {i.name: getattr(self, i.name) for i in self.__table__.columns}
        raise AssertionError('<%r> does not have attribute for __table__' % self)


class CommonMixin:
    """ 数据模型公共属性与方法"""
    __slots__ = ()

    is_deleted: Mapped[int | None] = \
        mapped_column(SmallInteger, server_default=text('0'), comment="是否删除: 0 未删除 1 已删除")
    create_time: Mapped[datetime | None] = \
        mapped_column(insert_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime | None] = \
        mapped_column(server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def save(self, db:Session):
        db.add(self)
        self.commit_or_rollback(db)
        return self

    def delete(self, db:Session, commit:bool=True):
        db.session.delete(self)
        if commit:
            self.commit_or_rollback(db)

    def update(self, db:Session, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(self, k) and getattr(self, k) != v:
                required_commit = True
                setattr(self, k, v)
        if required_commit:
            self.commit_or_rollback(db)
        return required_commit

    @classmethod
    def add_or_update(self, db:Session, where, **kwargs):
        record = self.query.filter_by(**where).first()
        if record:
            record.update(db, **kwargs)
        else:
            record = self(**kwargs).save(db)
        return record

    def commit_or_rollback(self, db):
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
