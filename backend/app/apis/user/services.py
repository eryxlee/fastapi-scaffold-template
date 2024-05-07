# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import user as user_model
from app.config import settings

from . import schemas


def get_user_by_id(db: Session, user_id: int):
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    return user

def get_user_by_name(db: Session, username: str) -> user_model.User:
    user = db.query(user_model.User).filter(user_model.User.name == username).first()
    return user

def create_user(db: Session, user_create: schemas.UserCreate):
    user = user_model.User(**user_create.model_dump())
    user.set_encrypt_password(user_create.password, settings.SALT)
    user.is_active = 0
    user.is_deleted = 0

    user.save(db)
    return user
