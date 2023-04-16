from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from litestar.contrib.sqlalchemy.base import AuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.lib import service

if TYPE_CHECKING:
    from app.domain.tasks import Task

__all__ = [
    "Project",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Project(AuditBase):
    project_slug: Mapped[str]
    title: Mapped[str]
    description: Mapped[str]
    start_date: Mapped[datetime] = m_col(default=datetime.now)
    end_date: Mapped[datetime] = m_col(default=datetime.now)
    tasks: Mapped[list["Task"] | None] = relationship("Task", back_populates="project", lazy="joined")


class Repository(SQLAlchemyRepository[Project]):
    model_type = Project


class Service(service.Service[Project]):
    repository_type = Project


WriteDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"id", "created", "updated", "tasks"})]]
ReadDTO = SQLAlchemyDTO[Project]
