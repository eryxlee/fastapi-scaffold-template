from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.api.todo.schemas import TodoCreate, TodoUpdate

# async def get_user_by_id(user_id: int):
#     query = select(User).where(User.id == user_id)
#     return await database.fetch_one(query)

# async def create_user(username: str, hashed_password: str):
#     query = User.insert().values(username=username, hashed_password=hashed_password)
#     return await database.execute(query)

async def get_todos(db: Session):
    query = select(Todo)
    return await db.fetch_all(query)

# async def get_todos_by_user_id(user_id: int):
#     query = select(Todo).where(Todo.owner_id == user_id)
#     return await database.fetch_all(query)

async def create_todo(db: Session, todo: TodoCreate):
    # query = Todo.insert().values(title=todo.title, description=todo.description, owner_id=1)

    from app.models.todo import Todo
    db_todo = Todo(**todo.model_dump(), id=None)
    db_todo.owner_id = 1
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

async def update_todo(db: Session, todo_id: int, todo: TodoUpdate):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.completed = todo.completed
        db.commit()
        db.refresh(db_todo)
        return db_todo

async def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
    return db_todo

