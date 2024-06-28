# -*- coding: utf-8 -*-

from abc import ABC
from typing import Generic, Optional, Type, TypeVar

from sqlmodel import SQLModel, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession as Session

ModelType = TypeVar("ModelType", bound=SQLModel)


class ServiceBase(Generic[ModelType], ABC):
    """基础服务类，提供服务公共方法."""

    def __init__(self, model: Type[ModelType], session: Session) -> None:
        self.session = session
        self.model = model

    async def get(self, id_: Optional[int] = None) -> ModelType | None:
        """检索对象."""
        statement = select(self.model).where(self.model.id == id_)
        results = await self.session.exec(statement=statement)
        return results.one_or_none()

    async def save(self, obj: ModelType) -> ModelType:
        """对象保存."""
        self.session.add(obj)
        await self.commit_or_rollback()
        await self.session.refresh(obj)
        return self

    async def delete(self, obj: ModelType, commit: bool = True) -> None:
        """对象删除."""
        await self.session.delete(obj)
        if commit:
            await self.commit_or_rollback()

    async def delete_by_id(self, id_: int) -> None:
        """按ID删除."""
        statement = delete(self.model).where(self.model.id == id_)

        await self.session.exec(statement=statement)
        await self.session.commit()

    async def update(self, obj: ModelType, **kwargs) -> ModelType:  # noqa: ANN003
        """对象更新."""
        required_commit = False
        for k, v in kwargs.items():
            if hasattr(obj, k) and getattr(obj, k) != v:
                required_commit = True
                setattr(obj, k, v)
        if required_commit:
            await self.commit_or_rollback()
        return obj

    async def add_or_update(self, obj: ModelType, where: str, **kwargs) -> ModelType:  # noqa: ANN003
        """新增或更新."""
        record = self.session.query.filter_by(**where).first()
        if record:
            await record.update(record, **kwargs)
        else:
            record = await self.save(ModelType(**kwargs))
        return record

    async def commit_or_rollback(self) -> None:
        """提交或回滚."""
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
