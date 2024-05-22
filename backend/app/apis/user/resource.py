# -*- coding: utf-8 -*-

from typing import Any
from fastapi import APIRouter, Depends

from app.models.user import *
from app.services.resource import ResourceService
from app.extensions.fastapi.pagination import PageQuery, PageSchemaOut

from .exception import *

router = APIRouter()


@router.get(
    "/",
    # dependencies=[Depends(check_jwt_token), Depends(get_current_active_superuser)],
    # response_model=UsersPublic,
)
async def read_resources(
        page: PageQuery = None,
        resource_service: ResourceService = Depends(ResourceService)
) -> Any:
    """
    Retrieve resources.
    """
    count = await resource_service.get_resource_list_count()
    resources = await resource_service.get_resource_list(page.offset, page.limit)
    page_out = PageSchemaOut.model_validate(page, update={"total": count})

    return {"data": resources, "page": page_out}
