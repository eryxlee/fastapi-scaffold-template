# -*- coding: utf-8 -*-

from typing import Any

from fastapi import APIRouter, Depends

from ...extensions.fastapi.pagination import PageModel, PageQueryParam
from ...services.resource import ResourceService

router = APIRouter()


@router.get(
    "/",
    # dependencies=[Depends(check_jwt_token), Depends(get_current_active_superuser)],
    # response_model=UsersPublic,
)
async def read_resources(
    page: PageQueryParam = None,
    resource_service: ResourceService = Depends(ResourceService),
) -> Any:
    """Retrieve resources."""
    count = await resource_service.get_resource_list_count()
    resources = await resource_service.get_resource_list(page.offset, page.limit)
    page_out = PageModel.model_validate(page, update={"total": count})

    return {"data": resources, "page": page_out}
