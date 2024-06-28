# -*- coding: utf-8 -*-

from typing import Any

from fastapi import APIRouter, Depends

from ...extensions.fastapi.pagination import PageModel, PageQueryParam
from ...services.role import RoleService

router = APIRouter()


@router.get(
    "/",
    # dependencies=[Depends(check_jwt_token), Depends(get_current_active_superuser)],
    # response_model=UsersPublic,
)
async def read_roles(
    page: PageQueryParam = None,
    role_service: RoleService = Depends(RoleService),
) -> Any:  # noqa: ANN401
    """Retrieve resources."""
    count = await role_service.get_role_list_count()
    roles = await role_service.get_role_list(page.offset, page.limit)
    page_out = PageModel.model_validate(page, update={"total": count})

    return {"data": roles, "page": page_out}
