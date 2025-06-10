from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from advanced_alchemy.filters import CollectionFilter, OrderBy
from litestar import Controller, delete, get, patch, post, put
from litestar.di import Provide
from litestar.exceptions import NotFoundException, HTTPException
from litestar.pagination import OffsetPagination
from litestar.params import Dependency
from litestar.status_codes import HTTP_200_OK
from structlog import getLogger

from app.db import models as m
from app.domain.accounts.deps import provide_user_service
from app.domain.accounts.guards import requires_active_user, requires_superuser
from app.domain.accounts.schemas import User as UserSchema
from app.domain.accounts.services import UserService
from app.domain.projects import urls
from app.domain.projects.dependencies import provide_project_service
from app.domain.projects.schemas import Project, ProjectCreate, ProjectStatusUpdate, ProjectUpdate
from app.domain.projects.services import ProjectService
from app.domain.teams.services import TeamService
from app.lib.deps import create_filter_dependencies, create_service_dependencies

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes


logger = getLogger()

__all__ = ["ProjectController"]


class ProjectController(Controller):

    guards = [requires_active_user]
    tags = ["Projects"]
    dependencies = (
        {"project_service": Provide(provide_project_service), "user_service": Provide(provide_user_service)}
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
        current_user: m.User,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[Project]:
        """Get a list of Models."""
        default_filters = [
            OrderBy(field_name="created_at", sort_order="desc"),
            CollectionFilter(field_name="is_archived", values=[False]),
        ] + (filters or [])
        if not (current_user.is_superuser):
            default_filters.append(m.Project.teams.any(m.Team.id.in_([team.team_id for team in current_user.teams])))
        project_objs, count = await project_service.list_and_count(*default_filters)

        return project_service.to_schema(data=project_objs, total=count, filters=default_filters, schema_type=Project)

    @post(urls.PROJECT_CREATE, guards=[requires_superuser])
    async def create_project(
        self,
        data: ProjectCreate,
        current_user: m.User,
        user_service: UserService,
        project_service: ProjectService,
        teams_service: TeamService,
    ) -> Project:
        """Create an `Model`."""

        data.owner_id = current_user.id

        teams: list[m.Team] | list = []
        internal_team = await teams_service.get_one_or_none(slug="internal")

        if internal_team and internal_team.id not in data.team_ids:
            teams.append(internal_team)

        for team_id in data.team_ids:
            team_obj = await teams_service.get_one_or_none(id=team_id)

            if team_obj is None:
                raise NotFoundException(detail="The Assigned Team not found", status_code=409)

            teams.append(team_obj)

        try:
            project_obj = await project_service.create(data)
            if len(teams) > 0:
                project_obj.teams = teams
                participants = []
                for team in teams:
                    for member in team.members:
                        db_obj = await user_service.get(member.user_id)
                        participants.append(db_obj.email)

                await project_service.assigned_participants(data=project_obj, participants=participants)
                
            return project_service.to_schema(data=project_obj, schema_type=Project)
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=409, detail="Failed to create project")

    @get(urls.PROJECT_DETAIL)
    async def get_project(self, project_service: ProjectService, id: UUID) -> Project:
        """Get Model by ID."""
        project_obj = await project_service.get_one_or_none(id=id)
        if project_obj is None:
            raise NotFoundException(detail="Project not found!", status_code=200)
        return project_service.to_schema(project_obj, schema_type=Project)

    @get(urls.PROJECT_DETAIL_BY_SLUG)
    async def get_project_by_slug(self, project_service: ProjectService, slug: str) -> Project:
        """Get Model by slug."""
        project_obj = await project_service.repository.get_by_slug(slug)
        if project_obj:
            return project_service.to_schema(project_obj, schema_type=Project)
        raise NotFoundException(detail="Project not found!", status_code=200)

    @put(urls.PROJECT_UPDATE, guards=[requires_superuser])
    async def update_project(
        self,
        data: ProjectUpdate,
        current_user: m.User,
        user_service: UserService,
        project_service: ProjectService,
        teams_service: TeamService,
        id: UUID,
    ) -> Project:
        """Update an Model."""

        project_obj = await project_service.get_one_or_none(id=id)

        if project_obj is None:
            raise NotFoundException(detail="Project Not found!", status_code=409)
        
        old_user_ids: set[str] = set()
        for team in project_obj.teams:
            for member in team.members:
                old_user_ids.add(member.user_id)

        updated_project = data.to_dict()
        latest_team_ids = set(updated_project.pop("team_ids"))
        project_obj = await project_service.update(item_id=id, data=updated_project)
        latest_teams: list[m.Team] = []
    
    
        new_user_ids: set[str] = set()
        for team_id in latest_team_ids:

            new_team = await teams_service.get_one_or_none(id=team_id)
            if new_team is None:
                raise NotFoundException(detail="Team Not found!", status_code=409)

            latest_teams.append(new_team)
            for member in new_team.members:
                new_user_ids.add(member.user_id)
                
        new_participant_ids = list(new_user_ids - old_user_ids)
        removed_participant_ids = list(old_user_ids - new_user_ids)
 
        if removed_participant_ids:
            removed_participants = [(await user_service.get(user_id)).email for user_id in removed_participant_ids]
            await project_service.removed_participants(data=project_obj, participants=removed_participants)
        if new_participant_ids:
            new_participants = [(await user_service.get(user_id)).email for user_id in new_participant_ids]
            await project_service.assigned_participants(data=project_obj, participants=new_participants)
        project_obj.teams = latest_teams

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

    @get(urls.PROJECT_ASSIGNEE, guards=[requires_superuser])
    async def get_project_assignee_by_slug(
        self, project_service: ProjectService, user_service: UserService, slug: str
    ) -> OffsetPagination[UserSchema]:
        project = await project_service.repository.get_by_slug(slug)
        if not project:
            raise NotFoundException("Project not found")

        if not project.teams:
            return user_service.to_schema(data=[], total=0, schema_type=UserSchema)

        users, total = await project_service.get_project_assignees(slug=slug)

        return user_service.to_schema(data=users, total=total, schema_type=UserSchema)
