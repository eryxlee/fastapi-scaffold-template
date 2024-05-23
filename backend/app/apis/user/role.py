# -*- coding: utf-8 -*-

from typing import Any
from fastapi import APIRouter, Depends

from app.models.user import *
from app.services.role import RoleService
from app.extensions.fastapi.pagination import PageQuery, PageSchemaOut

from .exception import *

router = APIRouter()


@router.get(
    "/",
    # dependencies=[Depends(check_jwt_token), Depends(get_current_active_superuser)],
    # response_model=UsersPublic,
)
async def read_roles(
        page: PageQuery = None,
        role_service: RoleService = Depends(RoleService)
) -> Any:
    """
    Retrieve resources.
    """
    count = await role_service.get_role_list_count()
    roles = await role_service.get_role_list(page.offset, page.limit)
    page_out = PageSchemaOut.model_validate(page, update={"total": count})

    return {"data": roles, "page": page_out}