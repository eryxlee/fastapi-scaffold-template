# -*- coding: utf-8 -*-

from jose import  jwt
from typing import Optional
from datetime import datetime, timedelta, UTC
from pydantic import ValidationError
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from app.models import get_db

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """

    :param data: 需要进行JWT令牌加密的数据（解密的时候会用到）
    :param expires_delta: 令牌有效期
    :return: token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    # 添加失效时间
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def check_jwt_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    验证token
    :param token:
    :return: 返回用户信息
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        username: str = payload.get("sub")
        # 通过解析得到的username,获取用户信息,并返回
        from app.apis.user.services import get_user_by_name
        return get_user_by_name(db, username)
    except (jwt.JWTError, jwt.ExpiredSignatureError, ValidationError):
        raise HTTPException(
            status_code=401,#status.HTTP_401_UNAUTHORIZED,
            detail={
                'code': 5000,
                'message': "Token Error",
                'data': "Token Error",
            }
        )
