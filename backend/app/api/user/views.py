# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import get_db
# from app.dependencies.auth import authenticate_user, get_current_active_user, oauth2_scheme
# from app.hashing import get_password_hash

from . import schemas
from app.models.user import User

router = APIRouter()

@router.post("/register/", response_model=schemas.User)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 验证用户是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # 创建新用户
    # hashed_password = get_password_hash(user_data.password)
    user = User(email=user_data.email, hashed_password=user_data.password, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# @router.post("/login/", response_model=dict)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = await authenticate_user(form_data)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.id}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# 其他用户相关的路由可以在这里继续定义，比如获取用户信息、更新用户信息等
