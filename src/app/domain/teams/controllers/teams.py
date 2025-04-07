"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide

from app.db import models as m
from app.db.models.enums import Status
from app.domain.sprintlogs.dependencies import provide_sprintlog_service
from app.domain.sprintlogs.service import SprintLogService
from app.domain.teams import urls
from app.domain.accounts.guards import requires_active_user
from app.domain.teams.guards import requires_team_membership, requires_team_ownership
from app.domain.teams.schemas import Team, TeamCreate, TeamStatistics, TeamUpdate
from app.domain.teams.services import TeamService
from app.domain.teams.deps import provide_team_service
from app.lib.deps import create_filter_dependencies

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service.pagination import OffsetPagination
    from litestar.params import Dependency, Parameter


class TeamController(Controller):
    """Teams."""

    tags = ["Teams"]
    dependencies = {
        "sprintlog_service": Provide(provide_sprintlog_service),
        "teams_service": Provide(provide_team_service),
    } | create_filter_dependencies(
        {
            "id_filter": UUID,
            "search": "name,description",
            "pagination_type": "limit_offset",
            "pagination_size": 20,
            "created_at": True,
            "updated_at": True,
            "sort_field": "created_at",
            "sort_order": "asc",
        },
    )

    @get(component="team/list", operation_id="ListTeams", path=urls.TEAM_LIST, guards=[requires_active_user])
    async def list_teams(
        self,
        teams_service: TeamService,
        current_user: m.User,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[Team]:
        """List teams that your account can access.."""

        if not current_user.is_superuser:
            filters.append(
                m.Team.id.in_(select(TeamMemberModel.team_id).where(TeamMemberModel.user_id == current_user.id)),  # type: ignore[arg-type]
            )
        results, total = await teams_service.list_and_count(*filters)
        return teams_service.to_schema(data=results, total=total, schema_type=Team, filters=filters)

    @post(operation_id="CreateTeam", path=urls.TEAM_CREATE)
    async def create_team(self, teams_service: TeamService, current_user: m.User, data: TeamCreate) -> Team:
        """Create a new team."""
        obj = data.to_dict()
        obj.update({"owner_id": current_user.id, "owner": current_user})
        db_obj = await teams_service.create(obj)
        return teams_service.to_schema(schema_type=Team, data=db_obj)

    @get(operation_id="GetTeam", guards=[requires_team_membership], path=urls.TEAM_DETAIL)
    async def get_team(
        self,
        teams_service: TeamService,
        team_id: Annotated[UUID, Parameter(title="Team ID", description="The team to retrieve.")],
    ) -> Team:
        """Get details about a team."""
        db_obj = await teams_service.get(team_id)
        return teams_service.to_schema(schema_type=Team, data=db_obj)

    @get(operation_id="GetTeamBySlug", path=urls.TEAM_SLUG, guards=[requires_team_membership])
    async def get_team_by_slug(self, teams_service: TeamService, slug: str) -> Team:
        "Get Project by Slug"
        db_obj = await teams_service.repository.get_by_slug(slug)
        return teams_service.to_schema(schema_type=Team, data=db_obj)

    @get(operation_id="GetTeamStatisticsBySlug", path=urls.TEAM_STATISTICS_SLUG)
    async def get_team_statistics_by_slug(
        self, teams_service: TeamService, sprintlog_service: SprintLogService, slug: str
    ) -> TeamStatistics:
        "Get Project by Slug"

        team_obj = await teams_service.repository.get_by_slug(slug)
        member_ids = [member.user_id for member in team_obj.members]

        completed_task = 0
        idle_task_count = 0
        in_progress_task_count = 0

        sprintlog_objs, task_count = await sprintlog_service.list_and_count(m.SprintLog.assignee_id.in_(member_ids))

        for sprintlog in sprintlog_objs:
            if sprintlog.status == Status.completed:
                completed_task += 1
            elif sprintlog.status == Status.new:
                idle_task_count += 1
            elif sprintlog.status == Status.started:
                in_progress_task_count += 1

        return TeamStatistics(
            member_count=len(team_obj.members),
            task_count=task_count,
            in_progress_task_count=in_progress_task_count,
            idle_task_count=idle_task_count,
            completed_task_count=completed_task,
        )

    @patch(operation_id="UpdateTeam", guards=[requires_team_ownership], path=urls.TEAM_UPDATE)
    async def update_team(
        self,
        data: TeamUpdate,
        teams_service: TeamService,
        team_id: Annotated[UUID, Parameter(title="Team ID", description="The team to update.")],
    ) -> Team:
        """Update a migration team."""
        db_obj = await teams_service.update(
            item_id=team_id,
            data=data.to_dict(),
        )
        return teams_service.to_schema(schema_type=Team, data=db_obj)

    @delete(operation_id="DeleteTeam", guards=[requires_team_ownership], path=urls.TEAM_DELETE)
    async def delete_team(
        self,
        teams_service: TeamService,
        team_id: Annotated[UUID, Parameter(title="Team ID", description="The team to delete.")],
    ) -> None:
        """Delete a team."""
        _ = await teams_service.delete(team_id)
