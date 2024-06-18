# -*- coding: utf-8 -*-

from typing import Any
from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.models.user import (
    User,
    UserPublic,
    UserListPage,
    UserUpdate,
    UserCreate
)
from app.services.user import UserService
from app.extensions.auth import get_current_user, PermissionChecker
from app.extensions.cache import request_key_builder
from app.extensions.fastapi.pagination import PageQueryParam

from .exception import UserNotFoundException, UsernameUsedException

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(PermissionChecker('sys:user:list'))],
    response_model=UserListPage,
)
@cache(expire=60, key_builder=request_key_builder)
async def read_users(
        page: PageQueryParam = None,
        user_service: UserService = Depends(UserService),
) -> Any:
    """ 读取所有用户信息"""
    count = await user_service.get_user_list_count()
    users = await user_service.get_user_list(page.offset, page.limit)
    from app.extensions.fastapi.pagination import PageModel
    page_out = PageModel.model_validate(page, update={"total": count})

    return UserListPage(users=users, page=page_out)


@router.get("/me", response_model=UserPublic)
@cache(expire=60, key_builder=request_key_builder)
async def user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """ 获取当前用户详情 """
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *,
    user_in: UserUpdate,
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
) -> Any:
    """ 修改当前用户信息"""

    if user_in.name:
        existing_user = await user_service.get_user_by_name(user_in.name)
        if existing_user and existing_user.id != current_user.id:
            raise UsernameUsedException()

    await user_service.patch_by_obj(current_user, user_in)

    return current_user


@router.post("/signup", response_model=UserPublic)
async def user_signup(
    user_in: UserCreate,
    user_service: UserService = Depends(UserService),
) -> Any:
    """ 注册新用户"""
    existing_user = await user_service.get_user_by_name(user_in.name)  # 获取用户信息
    if existing_user:
        raise UsernameUsedException()

    user_obj = await user_service.create(user_in)
    return user_obj


@router.get(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker('sys:user:list'))],
    response_model=UserPublic
)
@cache(expire=60, key_builder=request_key_builder)
async def read_user_by_id(
    user_id: int,
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
) -> Any:
    """ 根据id访问用户信息 """
    if user_id == current_user.id:
        return current_user
    return await user_service.get(user_id)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker('sys:user:update'))],
    response_model=UserPublic
)
async def update_user(
    *,
    user_id: int,
    user_in: UserUpdate,
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(get_current_user)
) -> Any:
    """ 修改用户信息 """
    if user_id == current_user.id:
        db_user = current_user
    else:
        db_user = await user_service.get(user_id)
    if not db_user:
        raise UserNotFoundException()
    if user_in.name:
        existing_user = await user_service.get_user_by_name(user_in.name)
        if existing_user and existing_user.id != user_id:
            raise UsernameUsedException()

    db_user = await user_service.patch_by_obj(db_user, user_in)
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker('sys:user:update'))],
)
async def user_delete(
    user_id: int,
    user_service: UserService = Depends(UserService),
) -> Any:
    """ 物理删除用户 """
    await user_service.delete_by_id(user_id)
    return {}
