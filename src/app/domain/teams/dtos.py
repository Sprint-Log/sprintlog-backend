from dataclasses import dataclass, field
from uuid import UUID

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DataclassDTO

from app.domain.teams.models import Team, TeamMember, TeamRoles
from app.lib import dto

__all__ = ["TeamCreate", "TeamCreateDTO", "TeamDTO", "TeamUpdate", "TeamUpdateDTO"]


# database model


class TeamDTO(SQLAlchemyDTO[Team]):
    config = dto.config(
        exclude={
            "members.team",
            "members.user",
            "members.created_at",
            "members.updated_at",
            "members.id",
            "members.user_name",
            "members.user_email",
            "invitations",
            "pending_invitations",
        },
        max_nested_depth=1,
    )


@dataclass
class TeamCreate:
    name: str
    description: str | None = None
    tags: list[str] = field(default_factory=list)


class TeamCreateDTO(DataclassDTO[TeamCreate]):
    """Team Create."""

    config = dto.config()


@dataclass
class TeamUpdate:
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class TeamUpdateDTO(DataclassDTO[TeamUpdate]):
    """Team Update."""

    config = dto.config()


# TeamMember


class TeamMemberDTO(SQLAlchemyDTO[TeamMember]):
    config = dto.config(exclude={"user", "team"})


@dataclass
class TeamMemberCreate:
    team_id: UUID
    user_id: UUID
    role: TeamRoles
    is_owner: bool


class TeamMemberCreateDTO(DataclassDTO[TeamMemberCreate]):
    """Team Create."""

    config = dto.config()


@dataclass
class TeamMemberEzCreate:
    team_name: str
    user_email: str
    role: TeamRoles
    is_owner: bool


class TeamMemberEzCreateDTO(DataclassDTO[TeamMemberEzCreate]):
    """Team Create."""

    config = dto.config()
