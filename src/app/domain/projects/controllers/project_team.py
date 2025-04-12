from __future__ import annotations

from structlog import getLogger
from uuid import UUID

from litestar import Controller, put
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from app.domain.accounts.guards import requires_active_user, requires_superuser
from app.domain.teams.services import TeamService

from app.domain.projects.dependencies import provide_project_service
from app.domain.projects.services import ProjectService
from app.domain.projects.schemas import Project, ProjectTeamModify
from app.domain.projects import urls

from app.lib.deps import create_filter_dependencies, create_service_dependencies

from app.db import models as m


logger = getLogger()

__all__ = ["ProjectTeamController"]


class ProjectTeamController(Controller):

    guards = [requires_active_user]
    tags = ["Project-Team"]
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

    @put(urls.PROJECT_ADD_TEAM, guards=[requires_superuser])
    async def add_team_to_project(
        self, data: ProjectTeamModify, project_service: ProjectService, teams_service: TeamService
    ) -> Project:
        """Add teh team to the project {project_id}."""

        project_obj = await project_service.get_one_or_none(id=data.project_id)
        team_obj = await teams_service.get_one_or_none(id=data.team_id)

        if project_obj is None:
            raise NotFoundException(detail="Project Not Found!", status_code=409)

        if team_obj is None:
            raise NotFoundException(detail="Team Not Found!", status_code=409)

        project_obj.teams.append(team_obj)
        project_obj = await project_service.update(item_id=project_obj.id, data=project_obj)
        return project_service.to_schema(project_obj, schema_type=Project)

    @put(urls.PROJECT_REMOVE_TEAM, guards=[requires_superuser])
    async def remove_team_to_project(
        self, data: ProjectTeamModify, project_service: ProjectService, teams_service: TeamService
    ) -> Project:
        """Remove the team from the project."""

        project_obj = await project_service.get_one_or_none(id=data.project_id)

        if project_obj is None:
            raise NotFoundException(detail="Project Not Found!", status_code=409)

        teams = [team for team in project_obj.teams if str(team.id) != data.team_id]

        project_obj = await project_service.update(item_id=project_obj.id, data={"teams": teams})

        return project_service.to_schema(project_obj, schema_type=Project)
