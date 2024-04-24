# -*- coding: utf-8 -*-

from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from app.models import get_db
from . import schemas, services


router = APIRouter()

# 依赖项，确保每个请求都有数据库会话可用 response_model=schemas.Todos
@router.get("/todos/", response_model=List[schemas.Todo], summary="Todo列表")
async def read_todos(db: Session = Depends(get_db)):
    todos = await services.get_todos(db)
    return todos # todos

@router.post("/todos/", response_model=schemas.Todo)
async def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = await services.create_todo(db, todo=todo)
    return db_todo

@router.get("/todos/{todo_id}", response_model=schemas.Todo)
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = await services.get_todo_by_id(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return db_todo

@router.put("/todos/{todo_id}", response_model=schemas.Todo)
async def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = await services.update_todo(db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return db_todo

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = await services.delete_todo(db, todo_id=todo_id)
    # if todo is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
