from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Sequence, Any
from uuid import UUID


from litestar import (
    Controller,
    delete,
    get,
    post,
    put,
)
from litestar.di import Provide
from litestar.params import Dependency

from app.domain.accounts.guards import requires_active_user
from app.domain.projects.dependencies import provide_project_service
from litestar.status_codes import HTTP_200_OK
from app.domain.projects.services import ProjectService

from uuid import UUID
from app.lib.deps import create_filter_dependencies
from structlog import getLogger
from app.domain.projects.dtos import WriteDTO, ReadDTO
from litestar import Response
from app.domain.projects import urls

from advanced_alchemy.filters import OrderBy

if TYPE_CHECKING:
    from app.db import models as m
    from advanced_alchemy.filters import FilterTypes


logger = getLogger()

if TYPE_CHECKING:
    logger.info("Yes it's a type check")

__all__ = ["ProjectController"]


class ProjectController(Controller):
    dto = WriteDTO
    return_dto = ReadDTO
    guards = [requires_active_user]
    tags = ["Projects API"]
    dependencies = {"service": Provide(provide_project_service)} | create_filter_dependencies(
        {
            "id_filter": UUID,
            "search": "name,email",
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "name",
            "sort_order": "asc",
        },
    )

    @get(urls.PROJECT_LIST)
    async def list_project(
        self,
        service: ProjectService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> Sequence[m.Project]:
        """Get a list of Models."""
        default_filters = [OrderBy(field_name="created_at", sort_order="desc")] + (filters or [])
        return await service.list(*default_filters)

    @post(urls.PROJECT_CREATE)
    async def create_project(
        self,
        data: m.Project,
        current_user: m.User,
        service: ProjectService,
    ) -> Response[Any]:
        """Create an `Model`."""

        data.owner_id = current_user.id
        try:
            project = await service.create(data)
            return Response(status_code=HTTP_200_OK, content=project.to_dict())
        except ValueError:
            return Response(status_code=409, content={"message": "Slug is not unique"})

    @get(urls.PROJECT_DETAIL)
    async def get_project(self, service: ProjectService, id: UUID) -> m.Project:
        """Get Model by ID."""
        return await service.get(id)

    @get(urls.PROJECT_DETAIL_BY_SLUG)
    async def get_project_by_slug(self, service: ProjectService, slug: str) -> m.Project:
        """Get Model by ID."""
        return await service.repository.get_by_slug(slug)

    @put(urls.PROJECT_UPDATE)
    async def update_project(
        self,
        data: m.Project,
        current_user: m.User,
        service: ProjectService,
        id: UUID,
    ) -> "m.Project":
        """Update an Model."""
        data.owner_id = current_user.id
        return await service.update(item_id=id, data=data)

    @delete(urls.PROJECT_DELETE, status_code=HTTP_200_OK)
    async def delete_project(self, service: ProjectService, id: UUID) -> m.Project:
        """Delete Author by ID."""
        return await service.delete(id)
