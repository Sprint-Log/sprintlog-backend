"""User Account Controllers."""

from __future__ import annotations


from sqlalchemy.orm import selectinload, contains_eager

from app.db import models as m
from app.domain.teams.services import TeamMemberService
from app.domain.teams.services import TeamService
from app.lib.deps import create_service_provider

__all__ = ["provide_team_service", "provide_team_member_service"]

provide_team_member_service = create_service_provider(
    TeamMemberService,
    load=[
        selectinload(m.TeamMember.team).options(contains_eager(m.Team.tags)),
        selectinload(m.TeamMember.user),
    ],
    error_messages={
        "duplicate_key": "This team member is already exists.",
        "integrity": "Team Member operation failed.",
    },
)


provide_team_service = create_service_provider(TeamService, load=[m.Team.tags, m.Team.members])
