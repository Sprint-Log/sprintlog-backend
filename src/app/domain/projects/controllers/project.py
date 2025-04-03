from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from structlog import getLogger
from uuid import UUID

from advanced_alchemy.filters import OrderBy, CollectionFilter
from litestar import Controller, delete, get, post, put, patch
from litestar.di import Provide
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK
from litestar.exceptions import NotFoundException, ValidationException
from litestar.pagination import OffsetPagination

from app.domain.accounts.guards import requires_active_user, requires_superuser
from app.domain.teams.services import TeamService

from app.domain.projects.dependencies import provide_project_service
from app.domain.projects.services import ProjectService
from app.domain.projects.schemas import ProjectCreate, Project, ProjectStatusUpdate, ProjectUpdate
from app.domain.projects import urls

from app.lib.deps import create_filter_dependencies, create_service_dependencies

from app.db import models as m

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes


logger = getLogger()

__all__ = ["ProjectController"]


class ProjectController(Controller):

    guards = [requires_active_user]
    tags = ["Projects"]
    dependencies = (
        {"project_service": Provide(provide_project_service)}
        | create_service_dependencies(
            TeamService,
            key="teams_service",
            load=[m.Team.tags, m.Team.members],
            filters={"id_filter": UUID},
        )
        | create_filter_dependencies(
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
    )

    @get(urls.PROJECT_LIST)
    async def list_project(
        self,
        project_service: ProjectService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[Project]:
        """Get a list of Models."""
        default_filters = [
            OrderBy(field_name="created_at", sort_order="desc"),
            CollectionFilter(field_name="is_archived", values=[False]),
        ] + (filters or [])

        project_objs, count = await project_service.list_and_count(*default_filters)

        return project_service.to_schema(data=project_objs, total=count, filters=default_filters, schema_type=Project)

    @post(urls.PROJECT_CREATE, guards=[requires_superuser])
    async def create_project(
        self,
        data: ProjectCreate,
        current_user: m.User,
        project_service: ProjectService,
        teams_service: TeamService,
    ) -> Project:
        """Create an `Model`."""

        data.owner_id = current_user.id
        team_ids = data.team_ids
        teams = []
        for team_id in team_ids:
            team_obj = await teams_service.get_one_or_none(id=team_id)

            if team_obj is None:
                raise NotFoundException(detail="The Assigned Team not found", status_code=409)

            teams.append(team_obj)

        try:
            project_obj = await project_service.create(data)
            if len(teams) > 0:
                project_obj.teams = teams
            return project_service.to_schema(data=project_obj, schema_type=Project)
        except Exception as e:
            logger.error(e)
            raise ValidationException(status_code=409, detail="Slug is not unique")

    @get(urls.PROJECT_DETAIL)
    async def get_project(self, project_service: ProjectService, id: UUID) -> Project:
        """Get Model by ID."""
        project_obj = await project_service.get_one_or_none(id=id)
        if project_obj is None:
            raise NotFoundException(detail="Project not found!", status_code=200)
        logger.info("Project")
        logger.info(project_obj.to_dict())
        return project_service.to_schema(project_obj, schema_type=Project)

    @get(urls.PROJECT_DETAIL_BY_SLUG)
    async def get_project_by_slug(self, project_service: ProjectService, slug: str) -> Project:
        """Get Model by slug."""
        logger.info("It is indeed in a slug")
        project_obj = await project_service.repository.get_by_slug(slug)
        if project_obj:
            return project_service.to_schema(project_obj, schema_type=Project)
        raise NotFoundException(detail="Project not found!", status_code=200)

    @put(urls.PROJECT_UPDATE, guards=[requires_superuser])
    async def update_project(
        self,
        data: ProjectUpdate,
        current_user: m.User,
        project_service: ProjectService,
        id: UUID,
    ) -> Project:
        """Update an Model."""
        data.owner_id = current_user.id
        project_obj = await project_service.update(item_id=id, data=data)
        return project_service.to_schema(project_obj, schema_type=Project)

    @patch(urls.PROJECT_STATUS_UPDATE, guards=[requires_superuser])
    async def update_project_status(
        self,
        project_service: ProjectService,
        data: ProjectStatusUpdate,
        id: UUID,
    ) -> Project:
        """Increase proejct status."""
        project = await project_service.get_one_or_none(id=id)
        if project is None:
            raise NotFoundException("Project not found!")

        project_obj = await project_service.update(item_id=id, data={"status": data.status})
        return project_service.to_schema(project_obj, schema_type=Project)

    @delete(urls.PROJECT_DELETE, status_code=HTTP_200_OK, guards=[requires_superuser])
    async def delete_project(self, project_service: ProjectService, id: UUID) -> None:
        """Delete Author by ID."""
        project_obj = await project_service.get_one_or_none(id=id)
        if project_obj:
            await project_service.update(item_id=id, data={"is_archived": True})
