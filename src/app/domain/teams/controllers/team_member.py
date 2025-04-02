"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, post, put
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from sqlalchemy.orm import contains_eager, selectinload
from structlog import getLogger

from app.db import models as m
from app.domain.accounts.deps import provide_user_service
from app.domain.teams import urls
from app.domain.teams.schemas import RemoveTeamMember, Team, TeamMember, TeamMemberModify, TeamMemberRole
from app.domain.teams.services import TeamMemberService, TeamService
from app.lib.deps import create_service_provider

if TYPE_CHECKING:
    from uuid import UUID

    from app.domain.accounts.services import UserService

logger = getLogger()


class TeamMemberController(Controller):
    """Team Members."""

    tags = ["Team Members"]
    dependencies = {
        "teams_service": create_service_provider(TeamService, load=[m.Team.tags, m.Team.members]),
        "team_members_service": create_service_provider(
            TeamMemberService,
            load=[
                selectinload(m.TeamMember.team).options(contains_eager(m.Team.tags)),
                selectinload(m.TeamMember.user),
            ],
        ),
        "users_service": Provide(provide_user_service),
    }

    @post(operation_id="AddMemberToTeam", path=urls.TEAM_ADD_MEMBER)
    async def add_member_to_team(
        self,
        teams_service: TeamService,
        users_service: UserService,
        data: list[TeamMemberModify],
        team_id: UUID = Parameter(title="Team ID", description="The team to update."),
    ) -> Team:
        """Add a member to a team. If the user is already a member, check their role and update if necessary."""
        team_obj = await teams_service.get(team_id)
        for user in data:
            user_obj = await users_service.get_one_or_none(id=user.user_id)

            if user_obj is None:
                raise NotFoundException("User not found!")
            member_obj = any(member.user_id == user_obj.id for member in team_obj.members)

            if member_obj:
                # Already a member
                continue
            team_obj.members.append(m.TeamMember(user_id=user_obj.id, role=user.role))
        team_obj = await teams_service.update(item_id=team_id, data=team_obj.to_dict())
        return teams_service.to_schema(schema_type=Team, data=team_obj)

    @put(operation_id="ModifyTeamMember", path=urls.TEAM_MODIFY_MEMBER)
    async def modify_team_member(
        self,
        teams_service: TeamService,
        team_members_service: TeamMemberService,
        data: list[TeamMemberModify],
        team_id: UUID = Parameter(title="Team ID", description="The team to update."),
    ) -> Team:
        team_obj = await teams_service.get(team_id)
        old_team_members = team_obj.members

        latest_user_ids = set(member.user_id for member in data)
        old_user_ids = set(str(member.user_id) for member in old_team_members)

        # Users to be removed (present before but not in latest list)
        user_ids_to_remove = old_user_ids - latest_user_ids
        remove_team_member_ids = [member.id for member in old_team_members if str(member.user_id) in user_ids_to_remove]

        latest_team_members: list[m.TeamMember] = []

        for member in data:

            existing_member = await team_members_service.get_one_or_none(team_id=team_id, user_id=member.user_id)

            if existing_member:
                if existing_member.role != member.role:
                    # Update role of the existing member
                    existing_member.role = member.role
                continue

            latest_team_members.append(m.TeamMember(team_id=team_id, user_id=member.user_id, role=member.role))

        # Create new members
        await team_members_service.create_many(latest_team_members)

        if user_ids_to_remove:

            await team_members_service.delete_many(remove_team_member_ids)

        return teams_service.to_schema(schema_type=Team, data=team_obj)

    @post(operation_id="RemoveMemberFromTeam", path=urls.TEAM_REMOVE_MEMBER)
    async def remove_member_from_team(
        self,
        teams_service: TeamService,
        team_members_service: TeamMemberService,
        users_service: UserService,
        data: RemoveTeamMember,
        team_id: UUID = Parameter(title="Team ID", description="The team to delete."),
    ) -> Team:
        """Revoke a members access to a team."""
        member_obj = await team_members_service.get_one_or_none(team_id=team_id, user_id=data.user_id)

        if member_obj is None:
            raise NotFoundException("User is not a member of this team.")

        _ = await team_members_service.delete(member_obj.id)

        team_obj = await teams_service.get(team_id)
        return teams_service.to_schema(schema_type=Team, data=team_obj)

    @post(operation_id="UpdateMemberRole", path=urls.TEAM_MEMBER_ROLE)
    async def update_member_role(
        self,
        team_members_service: TeamMemberService,
        data: TeamMemberRole,
        member_id: UUID = Parameter(title="Member ID", description="The member to update role."),
    ) -> TeamMember:
        """Update a team member role."""
        db_obj = await team_members_service.update(
            item_id=member_id,
            data=data.to_dict(),
        )
        return team_members_service.to_schema(schema_type=TeamMember, data=db_obj)
