"""Application Modules."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.jwt import OAuth2Login
from litestar.dto import DTOData
from litestar.pagination import OffsetPagination
from litestar.types import TypeEncodersMap
from pydantic import UUID4
from saq import Queue

from app.domain.accounts.dtos import (
    AccountLogin,
    AccountRegister,
    UserCreate,
    UserUpdate,
)
from app.domain.accounts.models import User
from app.domain.analytics.dtos import NewUsersByWeek
from app.domain.projects.models import ProjectService
from app.domain.sprintlogs.models import SprintlogService
from app.domain.tags.models import Tag
from app.domain.teams.models import Team, TeamMember

from . import (
    accounts,
    analytics,
    openapi,
    plugins,
    projects,
    room,
    security,
    sprintlogs,
    system,
    tags,
    teams,
    urls,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from litestar.types import ControllerRouterHandler


routes: list[ControllerRouterHandler] = [
    projects.controllers.ApiController,
    sprintlogs.controllers.ApiController,
    accounts.controllers.AccessController,
    accounts.controllers.AccountController,
    teams.controllers.TeamController,
    teams.controllers.TeamInvitationController,
    teams.controllers.TeamMemberController,
    room.controller.ApiController,
    analytics.controllers.StatsController,
    tags.controllers.TagController,
    system.controllers.SystemController,
]

__all__ = [
    "system",
    "accounts",
    "teams",
    "urls",
    "tags",
    "security",
    "routes",
    "openapi",
    "analytics",
    "plugins",
    "sprintlogs",
    "projects",
    "signature_namespace",
]

signature_namespace: Mapping[str, Any] = {
    "UUID": UUID,
    "UUID4": UUID4,
    "User": User,
    "Team": Team,
    "TeamMember": TeamMember,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "AccountLogin": AccountLogin,
    "AccountRegister": AccountRegister,
    "NewUsersByWeek": NewUsersByWeek,
    "Tag": Tag,
    "OAuth2Login": OAuth2Login,
    "OffsetPagination": OffsetPagination,
    "SprintlogService": SprintlogService,
    "ProjectService": ProjectService,
    "UserService": accounts.services.UserService,
    "TeamService": teams.services.TeamService,
    "TagService": tags.services.TagService,
    "TeamInvitationService": teams.services.TeamInvitationService,
    "TeamMemberService": teams.services.TeamMemberService,
    "DTOData": DTOData,
    "Queue": Queue,
    "TypeEncodersMap": TypeEncodersMap,
}
