# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.todo import Todo
from app.api.todo import schemas


async def get_todos(db: Session):
    query = db.query(Todo)
    return query.all()

async def get_todos_by_user_id(db: Session, user_id: int):
    query = db.query(Todo).filter(Todo.owner_id == user_id)
    return query.all()

async def get_todo_by_id(db: Session, todo_id: int):
    query = db.query(Todo).filter(Todo.id == todo_id)
    return query.first()

async def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = Todo(**todo.model_dump(), id=None, owner_id=1)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

async def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.completed = todo.completed
        db.commit()
        db.refresh(db_todo)
        return db_todo

async def delete_todo(db: Session, todo_id: int):
    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
