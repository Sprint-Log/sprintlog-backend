from __future__ import annotations

from datetime import datetime
from uuid import UUID  # noqa: TC003

import msgspec

from app.db.models.team_member import TeamRoles
from app.lib.schema import CamelizedBaseStruct


class TeamTag(CamelizedBaseStruct):
    id: UUID
    slug: str
    name: str


class TeamMember(CamelizedBaseStruct):
    user_id: UUID
    email: str
    name: str | None = None
    role: TeamRoles | None = TeamRoles.MEMBER
    is_owner: bool | None = False
    avatar_url: str | None = None


class TeamMemberDetail(CamelizedBaseStruct):
    id: UUID
    user_id: UUID
    email: str
    name: str | None = None
    role: TeamRoles | None = TeamRoles.MEMBER
    is_owner: bool | None = False
    avatar_url: str | None = None


class Team(CamelizedBaseStruct):
    id: UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    members: list[TeamMemberDetail] = []
    tags: list[TeamTag] = []


class TeamCreate(CamelizedBaseStruct):
    name: str
    description: str | None = None
    tags: list[str] = []


class TeamUpdate(CamelizedBaseStruct, omit_defaults=True):
    name: str | None | msgspec.UnsetType = msgspec.UNSET
    description: str | None | msgspec.UnsetType = msgspec.UNSET
    tags: list[str] | None | msgspec.UnsetType = msgspec.UNSET


class TeamMemberModify(CamelizedBaseStruct):
    """Team Member Modify."""

    user_id: str
    role: TeamRoles = TeamRoles.MEMBER


class RemoveTeamMember(CamelizedBaseStruct):
    """Team Member Modify."""

    user_id: str


class TeamStatistics(CamelizedBaseStruct):
    """Team Statistics."""

    member_count: int
    task_count: int
    in_progress_task_count: int
    idle_task_count: int
    completed_task_count: int


class TeamMemberRole(CamelizedBaseStruct):
    """Team Member Role"""

    role: TeamRoles = TeamRoles.MEMBER
