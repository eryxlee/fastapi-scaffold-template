# -*- coding: utf-8 -*-

from typing import  Generic, TypeVar

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession as Session

T = TypeVar('T')


class ServiceBase(Generic[T]):
    """ 数据库表公共属性模型定义 """
    @classmethod
    async def get(cls, session:Session, T, id: int = None) -> T | None:
        statement = select(T).where(T.id == id)
        results = await session.exec(statement=statement)
        return results.one_or_none()

    async def save(self, session:Session, obj:T):
        session.add(obj)
        await self.commit_or_rollback(session)
        await session.refresh(obj)
        return self

    async def delete(self, session:Session, obj:T, commit:bool=True):
        await session.delete(obj)
        if commit:
            await self.commit_or_rollback(session)

    @classmethod
    async def delete_without_select(cls, session:Session, T, id: int):
        statement = delete(T).where(T.id == id)

        await session.exec(statement=statement)
        await session.commit()

    async def update(self, session:Session, obj:T, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                required_commit = True
                setattr(obj, k, v)
        if required_commit:
            await self.commit_or_rollback(session)
        return required_commit

    @classmethod
    async def add_or_update(self, session:Session, obj:T, where, **kwargs):
        record = session.query.filter_by(**where).first()
        if record:
            await record.update(session, record, **kwargs)
        else:
            record = await self.save(session, T(**kwargs))
        return record

    async def commit_or_rollback(self, session):
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise
