from typing import Annotated
from uuid import UUID

from litestar.contrib.sqlalchemy.base import AuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.domain.projects import Project
from app.domain.users import User
from app.lib import service

__all__ = [
    "Task",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Task(AuditBase):
    title: Mapped[str]
    description: Mapped[str]
    progress: Mapped[int] = m_col(Integer, default=0)
    sprint_number: Mapped[int]
    priority: Mapped[int]
    status: Mapped[str]
    is_backlog: Mapped[bool]
    labels: Mapped[list[str] | None] = m_col(ARRAY(String))
    tags: Mapped[list[str] | None] = m_col(ARRAY(String))
    # Relationships
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    project_id: Mapped[UUID] = m_col(ForeignKey(Project.id))
    assignee: Mapped["User"] = relationship("User", back_populates="tasks", lazy="joined", foreign_keys=[assignee_id])
    project: Mapped["Project"] = relationship("Project", back_populates="tasks", foreign_keys=[project_id])


class Repository(SQLAlchemyRepository[Task]):
    model_type = Task


class Service(service.Service[Task]):
    repository_type = Task


WriteDTO = SQLAlchemyDTO[Annotated[Task, DTOConfig(exclude={"id", "created", "updated", "project"})]]
ReadDTO = SQLAlchemyDTO[Task]
