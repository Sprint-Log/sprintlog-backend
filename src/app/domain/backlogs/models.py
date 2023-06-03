import secrets
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any, cast
from uuid import UUID

from litestar.contrib.repository.filters import CollectionFilter
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import ARRAY, ForeignKey, SQLColumnExpression, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
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


class PriorityEnum(str, Enum):
    low = "🟢"
    med = "🟡"
    hi = "🔴"


class ProgressEnum(str, Enum):
    empty = "🟨🟨🟨"
    a_third = "🟩🟨🟨"
    two_third = "🟩🟩🟨"
    full = "🟩🟩🟩"


class StatusEnum(str, Enum):
    new = "🆕"
    started = "🛠️"
    checked_in = "🕛"
    completed = "✅"
    cancelled = "🚫"


class TagEnum(str, Enum):
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


class ItemType(str, Enum):
    backlog = "backlog"
    task = "task"
    draft = "draft"


class Backlog(orm.TimestampedDatabaseModel):
    title: Mapped[str]
    description: Mapped[str | None]
    slug: Mapped[str] = m_col(unique=True, index=True, info=dto_field(Mark.READ_ONLY))
    progress: Mapped[ProgressEnum] = m_col(String(length=50), default=ProgressEnum.empty, index=True)
    sprint_number: Mapped[int]
    priority: Mapped[PriorityEnum] = m_col(String(length=50), default=PriorityEnum.med, index=True)
    status: Mapped[StatusEnum] = m_col(String(length=50), default=StatusEnum.new, index=True)
    type: Mapped[ItemType] = m_col(String(length=50), default=ItemType.draft, index=True, server_default="backlog")
    category: Mapped[TagEnum] = m_col(String(length=50), default=TagEnum.features, index=True)
    order: Mapped[int] = m_col(default=0, server_default="0")
    est_days: Mapped[float]
    points: Mapped[int] = m_col(default=0, server_default="0")
    beg_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    due_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    labels: Mapped[list[str] | None] = m_col(ARRAY(String), nullable=True)
    # Relationships
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    owner_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    project_id: Mapped[str] = m_col(ForeignKey(Project.id))
    project: Mapped["Project"] = relationship(
        "Project", uselist=False, back_populates="backlogs", lazy="selectin", info=dto_field(Mark.READ_ONLY)
    )
    assignee: Mapped["User"] = relationship(
        "User",
        uselist=False,
        foreign_keys="Backlog.assignee_id",
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        foreign_keys="Backlog.owner_id",
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )
    audits: Mapped[list["BacklogAudit"]] = relationship("BacklogAudit", lazy="selectin", info=dto_field(Mark.READ_ONLY))
    project_slug: AssociationProxy[str] = association_proxy("project", "slug", info=dto_field(Mark.READ_ONLY))
    assignee_name: AssociationProxy[str] = association_proxy("assignee", "name", info=dto_field(Mark.READ_ONLY))
    owner_name: AssociationProxy[str] = association_proxy("owner", "name", info=dto_field(Mark.READ_ONLY))

    @hybrid_property
    def project_type(self) -> str:
        return f"{self.project.slug}_{self.type}"

    @project_type.inplace.expression  # type: ignore
    @classmethod
    def _project_type_expression(cls) -> SQLColumnExpression[String | None]:
        return cast("SQLColumnExpression[String | None]", Project.slug + "_" + cls.type)


Backlog.registry.update_type_annotation_map(
    {TagEnum: String, PriorityEnum: String, ProgressEnum: String, ItemType: String}
)


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
            slug = await self.repository.get_available_backlog_slug(backlog=data)
            if isinstance(slug, str):
                data.slug = slug
            data.due_date = await self.repository._get_due_date(data.beg_date, data.est_days)

        return await super().to_model(data, operation)

    async def filter_by_project_type(self, project_type: str) -> list[Backlog]:
        return await self.repository.list(CollectionFilter(field_name="project_type", values=[project_type]))


WriteDTO = SQLAlchemyDTO[
    Annotated[
        Backlog,
        DTOConfig(exclude={"id", "created", "updated", "_project_type_expression"}),
    ]
]
ReadDTO = SQLAlchemyDTO[Annotated[Backlog, DTOConfig(exclude={"_project_type_expression"})]]
