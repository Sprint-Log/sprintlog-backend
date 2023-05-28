import secrets
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from litestar.contrib.repository.filters import CollectionFilter
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.domain.accounts.models import User
from app.domain.projects.models import Project
from app.domain.projects.models import Repository as ProjectRepository
from app.lib.db import orm
from app.lib.repository import SQLAlchemyAsyncSlugRepository
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

__all__ = [
    "Backlog",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class PriorityEnum(Enum):
    low = "🟢"
    med = "🟡"
    hi = "🔴"


class ProgressEnum(Enum):
    empty = "🟨🟨🟨"
    a_third = "🟩🟨🟨"
    two_third = "🟩🟩🟨"
    full = "🟩🟩🟩"


class StatusEnum(Enum):
    new = "🔅"
    started = "🚧"
    checked_in = "✔️"
    completed = "✅"
    cancelled = "🚫"


class TagEnum(Enum):
    ideas = "💡"
    issues = "⚠️"
    maintenance = "🔨"
    finances = "💰"
    innovation = "🚀"
    bugs = "🐞"
    features = "🎁"
    security = "🔒"
    attention = "🚩"
    backend = "📡"
    database = "💾"
    desktop = "🖥️"
    mobile = "📱"
    intl = "🌍"
    design = "🎨"
    analytics = "📈"
    automation = "🤖"


class Backlog(orm.TimestampedDatabaseModel):
    title: Mapped[str]
    description: Mapped[str | None]
    slug: Mapped[str | None] = m_col(unique=True, nullable=True)
    progress: Mapped[ProgressEnum]
    sprint_number: Mapped[int]
    priority: Mapped[PriorityEnum]
    status: Mapped[StatusEnum]
    type: Mapped[str] = m_col(default="backlog", index=True, server_default="backlog")
    category: Mapped[TagEnum]
    est_days: Mapped[float]
    beg_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    due_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    # Relationships
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    owner_id: Mapped[UUID] = m_col(ForeignKey(User.id))
    project_id: Mapped[str] = m_col(ForeignKey(Project.id))
    project: Mapped["Project"] = relationship(
        "Project", uselist=False, back_populates="backlogs", lazy="joined", info=dto_field(Mark.READ_ONLY)
    )
    project_slug: AssociationProxy[str] = association_proxy("project", "slug")
    audits: Mapped[list["BacklogAudit"]] = relationship("BacklogAudit", lazy="selectin", info=dto_field(Mark.READ_ONLY))


class BacklogAudit(orm.TimestampedDatabaseModel):
    backlog_id: Mapped[UUID] = m_col(ForeignKey(Backlog.id))
    field_name: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]


class Repository(SQLAlchemyAsyncSlugRepository[Backlog]):
    model_type = Backlog

    async def get_available_backlog_slug(self, backlog: Backlog) -> str | None:
        project_slug: str | None = backlog.project_slug
        if not project_slug:
            project: Project = await ProjectRepository(session=self.session).get(backlog.project_id)
            project_slug = project.slug
        if not backlog.slug:
            token = secrets.token_hex(2)
            slug = f"{project_slug}-S{backlog.sprint_number}-{token}"
            if await self._is_slug_unique(slug):
                return slug
        return backlog.slug

    async def _get_due_date(self, beg_date: date, est_days: float = 3.0) -> date:
        return beg_date + timedelta(days=est_days)


class Service(SQLAlchemyAsyncRepositoryService[Backlog]):
    repository_type = Repository

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: Repository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

    async def to_model(self, data: Backlog | dict[str, Any], operation: str | None = None) -> Backlog:
        if isinstance(data, Backlog):
            data.slug = await self.repository.get_available_backlog_slug(backlog=data)
            data.due_date = await self.repository._get_due_date(data.beg_date, data.est_days)

        return await super().to_model(data, operation)

    async def get_by_project_slug(self, project_slug: str) -> list[Backlog]:
        return await self.repository.list(CollectionFilter(field_name="project_slug", values=[project_slug]))


WriteDTO = SQLAlchemyDTO[
    Annotated[
        Backlog,
        DTOConfig(
            exclude={
                "id",
                "created",
                "updated",
                # "project",
                "ref_id",
                # "audits",
                # "project_id",
                "assignee_id",
                "owner_id",
            }
        ),
    ]
]
ReadDTO = SQLAlchemyDTO[Annotated[Backlog, DTOConfig()]]
