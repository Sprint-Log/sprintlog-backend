from __future__ import annotations

from uuid import UUID
from datetime import UTC, date, datetime
from sqlalchemy import String, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from advanced_alchemy.base import UUIDAuditBase
from litestar.dto import Mark, dto_field
from typing import Any, TYPE_CHECKING
from advanced_alchemy.mixins import SlugKey
from .enums import ProjectStatus

if TYPE_CHECKING:
    from .user import User
    from .team import Team
    from .project_team import ProjectTeam

__all__ = ["Project"]


class Project(UUIDAuditBase, SlugKey):
    __tablename__ = "project"

    name: Mapped[str]
    description: Mapped[str]
    pin: Mapped[bool] = mapped_column(default=False)
    labels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    documents: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    start_date: Mapped[date] = mapped_column(default=datetime.now(tz=UTC).date())
    end_date: Mapped[date] = mapped_column(default=datetime.now(tz=UTC).date())
    sprint_weeks: Mapped[int | None] = mapped_column(default=2)
    sprint_amount: Mapped[int | None] = mapped_column(default=3)
    sprint_checkup_day: Mapped[int | None] = mapped_column(default=1)
    repo_urls: Mapped[list[str]] = mapped_column(ARRAY(String))
    status: Mapped[ProjectStatus] = mapped_column(
        String(length=50), nullable=False, default=ProjectStatus.NOT_STARTED, index=True
    )
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    plugin_meta: Mapped[dict | None] = mapped_column(
        default=dict,
        info=dto_field(Mark.READ_ONLY),
    )  # Relationships
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_account.id"), nullable=True)
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )
    teams: Mapped[list["Team"]] = relationship(secondary="project_team", back_populates="projects", lazy="selectin")

    def __init__(self, **kw: Any) -> None:
        super().__init__(**kw)
