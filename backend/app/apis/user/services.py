# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import user as user_model

from . import schemas


def get_user_by_id(db: Session, user_id: int):
    query = select(user_model.User).where(user_model.User.id == user_id)
    return db.execute(query).first()

def get_user_by_name(db: Session, username: str):
    query = select(user_model.User).where(user_model.User.name == username)
    return db.execute(query).first()

def create_user(db: Session, user_create: schemas.UserCreate):
    user = user_model.User(**user_create.model_dump())
    user.is_active = 0
    user.is_deleted = 0

    user.save(db)
    return user
