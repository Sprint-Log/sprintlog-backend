from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Sequence
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

from app.domain.projects.dependencies import provide_project_service
from litestar.status_codes import HTTP_200_OK

from app.domain.projects.services import ProjectService

from uuid import UUID
from app.lib.deps import create_filter_dependencies
from structlog import getLogger
from app.domain.projects.dtos import WriteDTO, ReadDTO

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
    path = "/api/projects"
    guards = []
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
    tags = ["Projects API"]

    DETAIL_ROUTE = "/{row_id:uuid}"

    @get()
    async def list_project(
        self,
        service: ProjectService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> Sequence[m.Project]:
        """Get a list of Models."""

        return await service.list(*filters)

    @post("create")
    async def create_project(
        self,
        data: m.Project,
        current_user: m.User,
        service: ProjectService,
    ) -> m.Project:
        """Create an `Model`."""

        data.owner_id = current_user.id
        return await service.create(data)

    @get(DETAIL_ROUTE)
    async def get_project(self, service: ProjectService, row_id: UUID) -> m.Project:
        """Get Model by ID."""
        return await service.get(row_id)

    @put(DETAIL_ROUTE)
    async def update_project(
        self,
        data: m.Project,
        current_user: m.User,
        service: ProjectService,
        row_id: UUID,
    ) -> "m.Project":
        """Update an Model."""
        data.owner_id = current_user.id
        return await service.update(item_id=row_id, data=data)

    @delete(DETAIL_ROUTE, status_code=HTTP_200_OK)
    async def delete_project(self, service: ProjectService, row_id: "UUID") -> m.Project:
        """Delete Author by ID."""
        return await service.delete(row_id)
