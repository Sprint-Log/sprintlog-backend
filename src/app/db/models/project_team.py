from __future__ import annotations

from uuid import UUID  # noqa: TC003

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["ProjectTeam"]


class ProjectTeam(UUIDAuditBase):
    """Team Membership."""

    __tablename__ = "project_team"
    __table_args__ = (UniqueConstraint("project_id", "team_id"),)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("project.id", ondelete="cascade"), nullable=False)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id", ondelete="cascade"), nullable=False)
