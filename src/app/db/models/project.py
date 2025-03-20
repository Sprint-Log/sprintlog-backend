from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .oauth_account import UserOauthAccount
    from .team_member import TeamMember
    from .user_role import UserRole




class Project(orm.TimestampedDatabaseModel):
    slug: Mapped[str] = m_col(unique=True)
    name: Mapped[str]
    description: Mapped[str]
    pin: Mapped[bool] = m_col(default=False)
    labels: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    documents: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    start_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    sprint_weeks: Mapped[int | None] = m_col(default=2)
    sprint_amount: Mapped[int | None] = m_col(default=3)
    sprint_checkup_day: Mapped[int | None] = m_col(default=1)
    repo_urls: Mapped[list[str]] = m_col(ARRAY(String))
    plugin_meta: Mapped[dict | None] = m_col(
        default=lambda: dict,
        info=dto_field(Mark.READ_ONLY),
    )  # Relationships
    owner_id: Mapped[UUID | None] = m_col(ForeignKey(User.id), nullable=True)
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )

    def __init__(self, **kw: Any) -> None:
        super().__init__(**kw)
