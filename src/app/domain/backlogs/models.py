import secrets
from datetime import UTC, date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any
from uuid import UUID

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import Connection, ForeignKey, event
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Mapped, Mapper, Session, relationship
from sqlalchemy.orm import mapped_column as m_col
from sqlalchemy.orm.attributes import History, get_history
from sqlalchemy.orm import attributes
from sqlalchemy import inspect
from app.domain.accounts.models import User
from app.domain.projects.models import Project
from app.lib.db import orm
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
    ref_id: Mapped[str] = m_col(unique=True,default=secrets.token_hex(6))
    progress: Mapped[ProgressEnum]
    sprint_number: Mapped[int]
    priority: Mapped[PriorityEnum]
    status: Mapped[StatusEnum]
    is_task: Mapped[bool]
    category: Mapped[TagEnum]
    est_days: Mapped[float]
    beg_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    due_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date)
    # Relationships
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    owner_id: Mapped[UUID] = m_col(ForeignKey(User.id))
    project_id: Mapped[str] = m_col(ForeignKey(Project.id))
    project: Mapped["Project"] = relationship( "Project",uselist=False, back_populates="backlogs", lazy="joined", info=dto_field(Mark.READ_ONLY))
    audits: Mapped[list["BacklogAudit"]] = relationship("BacklogAudit", lazy="selectin",info=dto_field(Mark.READ_ONLY))
    project_slug: AssociationProxy[str] = association_proxy("project", "slug")
    assignee: AssociationProxy[str] = association_proxy("user", "name")
    owner: AssociationProxy[str] = association_proxy("user", "name")

    @hybrid_method
    async def gen_refid_slug(self,project_slug) -> str:
        slug = project_slug
        sprint_number = self.sprint_number
        # Take the first 8 characters of the UUID and remove any hyphens
        return f"{slug}-S{sprint_number}-{self.ref_id}"

    @hybrid_method
    async def gen_due_date(self, beg_date: date, est_days: float) -> date:
        return beg_date + timedelta(days=est_days)


class BacklogAudit(orm.TimestampedDatabaseModel):
    backlog_id: Mapped[UUID] = m_col(ForeignKey(Backlog.id))
    field_name: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]

class Repository(SQLAlchemyAsyncRepository[Backlog]):
    model_type = Backlog


class Service(SQLAlchemyAsyncRepositoryService[Backlog]):
    repository_type = Repository

    async def create(self, data: Backlog) -> Backlog:
        data.due_date = await data.gen_due_date(data.beg_date, data.est_days)
        data = await super().create(data)
        data.ref_id = await data.gen_refid_slug(project_slug=data.project_slug)
        return await super().update(item_id=data.id,data=data)
    async def to_model(self, data: Backlog, operation: str | None = None) -> Backlog:
        return await super().to_model(data, operation)


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
