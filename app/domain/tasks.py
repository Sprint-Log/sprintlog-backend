from typing import Annotated
from uuid import UUID

from litestar.contrib.sqlalchemy.base import AuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

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
    project_slug: Mapped[str]
    priority: Mapped[int]
    status: Mapped[str]
    is_backlog: Mapped[bool]
    labels: Mapped[list | None]
    tags: Mapped[list | None]
    assigner: Mapped[User | None] = relationship(back_populates="tasks_managed", foreign_keys=["assigner_id"])
    assignee: Mapped[User | None] = relationship(back_populates="tasks_owned", foreign_keys=["assignee_id"])
    assigner_id: Mapped[UUID | None] = m_col(ForeignKey("user.id"))
    assignee_id: Mapped[UUID | None] = m_col(ForeignKey("user.id"))


class Repository(SQLAlchemyRepository[Task]):
    model_type = Task


class Service(service.Service[Task]):
    repository_type = Task


WriteDTO = SQLAlchemyDTO[Annotated[Task, DTOConfig(exclude={"id", "created", "updated", "nationality"})]]
ReadDTO = SQLAlchemyDTO[Task]
