from __future__ import annotations


from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import Field
from app.lib.schema import CamelizedBaseStruct


__all__ = ["Project"]


class Project(CamelizedBaseStruct):
    """Project schemas."""

    slug: str
    name: str
    description: str
    pin: bool = False
    labels: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    start_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    end_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    sprint_weeks: Optional[int] = 2
    sprint_amount: Optional[int] = 3
    sprint_checkup_day: Optional[int] = 1
    repo_urls: list[str] = Field(default_factory=list)
    plugin_meta: dict[str, Any] | None = None
    owner: str | None = None
    owner_id: UUID | None = None


class ProjectCreate(CamelizedBaseStruct):
    """
    Schema used for creating a new Project.
    Excludes:
      - id
      - created_at
      - updated_at
      - sprintlogs
      - plugin_meta
      - owner
    """

    slug: str
    name: str
    description: str
    pin: bool = False
    labels: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    start_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    end_date: date = Field(default_factory=lambda: datetime.utcnow().date())
    sprint_weeks: Optional[int] = 2
    sprint_amount: Optional[int] = 3
    sprint_checkup_day: Optional[int] = 1
    repo_urls: list[str] = Field(default_factory=list)


class ProjectUpdate(CamelizedBaseStruct):
    """Schema used when updating an existing Project."""

    # You could make fields optional here as well, if partial updates are allowed
    pass


class ProjectRead(CamelizedBaseStruct):
    """Schema used to read a Project from the database."""

    id: UUID
    owner_id: Optional[UUID] = None

    class Config:
        orm_mode = True
        # ensures that reading from SQLAlchemy objects via ORM is allowed
