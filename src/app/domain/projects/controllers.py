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
from litestar.status_codes import HTTP_200_OK
from litestar.exceptions import NotFoundException
from litestar import Response, patch

from app.db.models.enums import ProjectStatus
from app.domain.accounts.guards import requires_active_user, requires_superuser
from app.domain.projects.dependencies import provide_project_service
from app.domain.projects.services import ProjectService

from uuid import UUID
from app.lib.deps import create_filter_dependencies
from structlog import getLogger
from app.domain.projects.dtos import WriteDTO, ReadDTO
from app.domain.projects import urls

from advanced_alchemy.filters import OrderBy, CollectionFilter

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
        default_filters = [
            OrderBy(field_name="created_at", sort_order="desc"),
            CollectionFilter(field_name="is_archived", values=[False]),
        ] + (filters or [])
        return await service.list(*default_filters)

    @post(urls.PROJECT_CREATE, guards=[requires_superuser])
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

    @put(urls.PROJECT_UPDATE, guards=[requires_superuser])
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

    @patch(urls.PROJECT_STATUS_UP, guards=[requires_superuser])
    async def project_status_up(
        self,
        service: ProjectService,
        id: UUID,
    ) -> "m.Project":
        """Increase proejct status."""
        project = await service.get_one_or_none(id=id)
        if project is None:
            raise NotFoundException("Project not found!")

        if project.status == ProjectStatus.NOT_STARTED:
            project.status = ProjectStatus.ACTIVE
        elif project.status == ProjectStatus.ACTIVE:
            project.status = ProjectStatus.COMPLETED
        else:
            return project

        return await service.update(item_id=id, data={"status": project.status})

    @patch(urls.PROJECT_STATUS_DOWN, guards=[requires_superuser])
    async def project_status_down(
        self,
        service: ProjectService,
        id: UUID,
    ) -> "m.Project":
        """Increase proejct status."""
        project = await service.get_one_or_none(id=id)
        if project is None:
            raise NotFoundException("Project not found!")

        if project.status == ProjectStatus.ACTIVE:
            project.status = ProjectStatus.NOT_STARTED
        elif project.status == ProjectStatus.COMPLETED:
            project.status = ProjectStatus.ACTIVE
        else:
            return project

        return await service.update(item_id=id, data={"status": project.status})

    @delete(urls.PROJECT_DELETE, status_code=HTTP_200_OK, guards=[requires_superuser])
    async def delete_project(self, service: ProjectService, id: UUID) -> None:
        """Delete Author by ID."""
        project_obj = await service.get_one_or_none(id=id)
        if project_obj:
            await service.update(item_id=id, data={"is_archived": True})
