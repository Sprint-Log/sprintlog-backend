from uuid import UUID
from datetime import UTC, date, datetime
from sqlalchemy import ForeignKey, String, ARRAY, ForeignKey, SQLColumnExpression
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from advanced_alchemy.base import UUIDAuditBase
from litestar.dto import Mark, dto_field
 
from app.domain.sprintlogs.schemas import (
    Progress,
    Priority,
    Status,
    ItemType,
    Category,
)
from typing import TYPE_CHECKING, cast
from sqlalchemy.ext.hybrid import hybrid_property
 

if TYPE_CHECKING:
    from app.db.models import User, Project, Audit

class SprintLog(UUIDAuditBase):
    title: Mapped[str] = mapped_column(String(length=200), index=True)
    description: Mapped[str | None]
    slug: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        index=True,
        info=dto_field(Mark.READ_ONLY),
    )
    progress: Mapped[Progress] = mapped_column(
        String(length=50),
        default=Progress.empty,
        index=True,
    )
    sprint_number: Mapped[int]
    priority: Mapped[Priority] = mapped_column(
        String(length=50),
        default=Priority.med,
        index=True,
    )
    status: Mapped[Status] = mapped_column(
        String(length=50),
        default=Status.new,
        index=True,
    )
    type: Mapped[ItemType] = mapped_column(
        String(length=50),
        default=ItemType.draft,
        index=True,
    )
    category: Mapped[Category] = mapped_column(
        String(length=50),
        default=Category.features,
        index=True,
    )
    order: Mapped[int] = mapped_column(default=0)
    est_days: Mapped[float]
    points: Mapped[int] = mapped_column(default=0)
    beg_date: Mapped[date] = mapped_column(default=datetime.now(tz=UTC).date)
    end_date: Mapped[date] = mapped_column(default=datetime.now(tz=UTC).date)
    due_date: Mapped[date] = mapped_column(default=datetime.now(tz=UTC).date)
    labels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    plugin_meta: Mapped[dict | None] = mapped_column(
        default=lambda: dict,
        info=dto_field(Mark.READ_ONLY),
        nullable=True,
    )  # Relationships
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey(User.id))
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey(User.id))
    project_slug: Mapped[str] = mapped_column(ForeignKey(Project.slug), nullable=True)
    project: Mapped["Project"] = relationship(
        "Project",
        uselist=False,
        lazy="joined",
        info=dto_field(Mark.READ_ONLY),
    )
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
    audits: Mapped[list["Audit"]] = relationship(
        "Audit",
        lazy="noload",
        info=dto_field(Mark.READ_ONLY),
    )
    project_name: AssociationProxy[str] = association_proxy(
        "project",
        "name",
    )
    pin: AssociationProxy[bool] = association_proxy(
        "project",
        "pin",
        info=dto_field(Mark.READ_ONLY),
    )
    assignee_name: AssociationProxy[str] = association_proxy(
        "assignee",
        "name",
        info=dto_field(Mark.READ_ONLY),
    )
    owner_name: AssociationProxy[str] = association_proxy(
        "owner",
        "name",
        info=dto_field(Mark.READ_ONLY),
    )

    @hybrid_property
    def project_type(self) -> str:
        return f"{self.project.slug}_{self.type}"

    @project_type.inplace.expression  # type: ignore
    @classmethod
    def _project_type_expression(cls) -> SQLColumnExpression[String | None]:
        return cast(
            "SQLColumnExpression[String | None]",
            cls.project_slug + "_" + cls.type,
        )
        
        
SprintLog.registry.update_type_annotation_map(
    {Category: String, Priority: String, Progress: String, ItemType: String},
)
