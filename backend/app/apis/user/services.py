# -*- coding: utf-8 -*-

from sqlmodel import Session, select
from fastapi import Depends

from app.models import get_db
from app.commons.enums import *
from app.models.user import *


class UserService:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_id(self, user_id: int = None) -> User | None:
        statement = select(User).where(User.id == user_id)
        results = self.session.exec(statement=statement)
        return results.one_or_none()

    def get_user_by_name(self, username: str = None)-> User | None:
        statement = select(User).where(User.name == username)
        results = self.session.exec(statement=statement)
        return results.one_or_none()

    def create_user(self, user_create: UserCreate) -> User:
        user = User(**user_create.model_dump())
        user.password = User.encrypt_password(user_create.password)
        user.is_active = UserAvailableStatus.NOT_SET
        user.is_deleted = DeleteStatus.NOT_SET

        user.save(self.session)
        return user
