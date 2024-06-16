# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import  Generic, Type, TypeVar

from sqlmodel import select, delete, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as Session

ModelType = TypeVar('ModelType', bound=SQLModel)


class ServiceBase(Generic[ModelType], ABC):
    """
    基础服务类，提供服务公共方法
    """
    def __init__(self, model:Type[ModelType], session:Session):
        self.session = session
        self.model = model

    async def get(self, id: int = None) -> ModelType | None:
        statement = select(self.model).where(self.model.id == id)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def save(self, obj:ModelType):
        self.session.add(obj)
        await self.commit_or_rollback()
        await self.session.refresh(obj)
        return self

    async def delete(self, obj:ModelType, commit:bool=True):
        await self.session.delete(obj)
        if commit:
            await self.commit_or_rollback()

    async def delete_by_id(self, id: int):
        statement = delete(self.model).where(self.model.id == id)

        await self.session.exec(statement=statement)
        await self.session.commit()

    async def update(self, obj:ModelType, **kwargs):
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                required_commit = True
                setattr(obj, k, v)
        if required_commit:
            await self.commit_or_rollback()
        return required_commit

    async def add_or_update(self, obj:ModelType, where, **kwargs):
        record = self.session.query.filter_by(**where).first()
        if record:
            await record.update(record, **kwargs)
        else:
            record = await self.save(ModelType(**kwargs))
        return record

    async def commit_or_rollback(self):
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
