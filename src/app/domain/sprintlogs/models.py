import secrets
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any, cast
from uuid import UUID

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import ARRAY, ForeignKey, SQLColumnExpression, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.domain.accounts.models import User
from app.domain.projects.models import Project
from app.lib.db import orm
from app.lib.plugin import SprintlogPlugin
from app.lib.repository import SQLAlchemyAsyncSlugRepository
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

__all__ = [
    "SprintLog",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class PriorityEnum(StrEnum):
    low = "🟢"
    med = "🟡"
    hi = "🔴"


class ProgressEnum(StrEnum):
    empty = "⬜⬜⬜"
    a_third = "🟩⬜⬜"
    two_third = "🟩🟩⬜"
    full = "🟩🟩🟩"


class StatusEnum(StrEnum):
    new = "☀️"
    started = "🛠️"
    checked_in = "🔳"
    completed = "✅"
    cancelled = "🚫"


class TagEnum(StrEnum):
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


class ItemType(StrEnum):
    backlog = "backlog"
    task = "task"
    draft = "draft"
    self = "self"


class SprintLog(orm.TimestampedDatabaseModel):
    title: Mapped[str] = m_col(String(length=200), index=True)
    description: Mapped[str | None]
    slug: Mapped[str] = m_col(String(length=50), unique=True, index=True, info=dto_field(Mark.READ_ONLY))
    progress: Mapped[ProgressEnum] = m_col(String(length=50), default=ProgressEnum.empty, index=True)
    sprint_number: Mapped[int]
    priority: Mapped[PriorityEnum] = m_col(String(length=50), default=PriorityEnum.med, index=True)
    status: Mapped[StatusEnum] = m_col(String(length=50), default=StatusEnum.new, index=True)
    type: Mapped[ItemType] = m_col(String(length=50), default=ItemType.draft, index=True)
    category: Mapped[TagEnum] = m_col(String(length=50), default=TagEnum.features, index=True)
    order: Mapped[int] = m_col(default=0)
    est_days: Mapped[float]
    points: Mapped[int] = m_col(default=0)
    beg_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    due_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    labels: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    plugin_meta: Mapped[dict] = m_col(default=lambda: dict, info=dto_field(Mark.READ_ONLY))  # Relationships
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    owner_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    project_slug: Mapped[str] = m_col(ForeignKey(Project.slug), nullable=True)
    project: Mapped["Project"] = relationship("Project", uselist=False, lazy="selectin", info=dto_field(Mark.READ_ONLY))
    assignee: Mapped["User"] = relationship(
        "User",
        uselist=False,
        foreign_keys=assignee_id,
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        foreign_keys=owner_id,
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )
    audits: Mapped[list["Audit"]] = relationship("Audit", lazy="noload", info=dto_field(Mark.READ_ONLY))
    project_name: AssociationProxy[str] = association_proxy("project", "name", info=dto_field(Mark.READ_ONLY))
    pin: AssociationProxy[bool] = association_proxy("project", "pin", info=dto_field(Mark.READ_ONLY))
    assignee_name: AssociationProxy[str] = association_proxy("assignee", "name", info=dto_field(Mark.READ_ONLY))
    owner_name: AssociationProxy[str] = association_proxy("owner", "name", info=dto_field(Mark.READ_ONLY))

    @hybrid_property
    def project_type(self) -> str:
        return f"{self.project.slug}_{self.type}"

    @project_type.inplace.expression  # type: ignore
    @classmethod
    def _project_type_expression(cls) -> SQLColumnExpression[String | None]:
        return cast("SQLColumnExpression[String | None]", cls.project_slug + "_" + cls.type)


SprintLog.registry.update_type_annotation_map(
    {TagEnum: String, PriorityEnum: String, ProgressEnum: String, ItemType: String}
)


class Audit(orm.TimestampedDatabaseModel):
    backlog_id: Mapped[UUID] = m_col(ForeignKey(SprintLog.id))
    field_name: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]


WriteDTO = SQLAlchemyDTO[Annotated[SprintLog, DTOConfig(exclude={"id", "created_at", "updated_at"})]]
ReadDTO = SQLAlchemyDTO[Annotated[SprintLog, DTOConfig(exclude={"project", "audits"})]]


class Repository(SQLAlchemyAsyncSlugRepository[SprintLog]):
    model_type = SprintLog

    async def get_available_sprintlog_slug(self, sprintlog: SprintLog) -> str | None:
        project_slug: str | None = sprintlog.project_slug
        if not sprintlog.slug:
            token = secrets.token_hex(2)
            slug = f"{project_slug}-S{sprintlog.sprint_number}-{token}"
            if await self._is_slug_unique(slug):
                return slug
        return sprintlog.slug

    async def _get_due_date(self, beg_date: date, est_days: float = 3.0) -> date:
        return beg_date + timedelta(days=est_days)


class Service(SQLAlchemyAsyncRepositoryService[SprintLog]):
    repository_type = Repository
    plugins: set[SprintlogPlugin] = set()

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: Repository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)

    async def to_model(self, data: SprintLog | dict[str, Any], operation: str | None = None) -> SprintLog:
        if isinstance(data, SprintLog):
            slug = await self.repository.get_available_sprintlog_slug(sprintlog=data)
            if isinstance(slug, str):
                data.slug = slug
            data.due_date = await self.repository._get_due_date(data.beg_date, data.est_days)

        return await super().to_model(data, operation)

    async def create(self, data: SprintLog | dict[str, Any]) -> SprintLog:
        # Call the before_create hook for each registered plugin
        for plugin in self.plugins:
            data = await plugin.before_create(data=data)

        obj = await super().create(data)
        # Call the after_create hook for each
        for plugin in self.plugins:
            after = await plugin.after_create(data=obj)
            obj = await super().update(obj.id, after)

        return obj

    async def update(self, item_id: Any, data: SprintLog | dict[str, Any]) -> SprintLog:
        # Call the before_update hook for each registered plugin
        for plugin in self.plugins:
            data = await plugin.before_update(item_id=item_id, data=data)

        obj: SprintLog = await super().update(item_id, data)

        # Call the after_update hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_update(data=obj)

        return obj

    async def delete(self, item_id: Any) -> SprintLog:
        # Call the before_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj: SprintLog = await self.repository.delete(item_id)

        # Call the after_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj
