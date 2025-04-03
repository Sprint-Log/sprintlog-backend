from __future__ import annotations


from typing import Any, Optional
from uuid import UUID
from datetime import date
from app.db.models.enums import ProjectStatus
from app.lib.schema import CamelizedBaseStruct
from app.domain.teams.schemas import Team

__all__ = ["ProjectCreate", "ProjectUpdate", "ProjectStatusUpdate"]


class ProjectCreate(CamelizedBaseStruct):
    """Project schemas."""

    slug: str
    name: str
    description: str
    pin: bool = False
    labels: list[str] = []
    documents: list[str] = []
    sprint_weeks: Optional[int] = 2
    sprint_amount: Optional[int] = 3
    sprint_checkup_day: Optional[int] = 1
    repo_urls: list[str] = []
    plugin_meta: dict[str, Any] | None = None
    owner_id: Optional[UUID] = None
    is_archived: bool = False
    status: Optional[ProjectStatus] = ProjectStatus.NOT_STARTED
    team_ids: list[str] = []


class Project(CamelizedBaseStruct):
    id: UUID
    slug: str
    name: str
    description: str
    start_date: date
    end_date: date
    pin: bool = False
    labels: list[str] = []
    documents: list[str] = []
    sprint_weeks: Optional[int] = 2
    sprint_amount: Optional[int] = 3
    sprint_checkup_day: Optional[int] = 1
    repo_urls: list[str] = []
    owner_id: UUID | None = None
    is_archived: bool = False
    status: Optional[ProjectStatus] = ProjectStatus.NOT_STARTED
    teams: Optional[list[Team]] = None


class ProjectUpdate(CamelizedBaseStruct):
    """Schema used when updating an existing Project."""

    id: UUID
    slug: str
    name: str
    start_date: date
    end_date: date
    description: str
    pin: bool = False
    labels: list[str] = []
    documents: list[str] = []
    sprint_weeks: Optional[int] = 2
    sprint_amount: Optional[int] = 3
    sprint_checkup_day: Optional[int] = 1
    repo_urls: list[str] = []
    plugin_meta: dict[str, Any] | None = None
    owner: str | None = None
    owner_id: UUID | None = None
    is_archived: bool = False
    status: Optional[ProjectStatus] = ProjectStatus.NOT_STARTED
    team_ids: list[str] = []


class ProjectTeamModify(CamelizedBaseStruct):
    team_id: str
    project_id: str


class ProjectStatusUpdate(CamelizedBaseStruct):
    status: ProjectStatus
