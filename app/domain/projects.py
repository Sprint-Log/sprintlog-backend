from datetime import datetime
from typing import Annotated

from litestar.contrib.sqlalchemy.base import AuditBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column as m_col

from app.lib import service

__all__ = [
    "Project",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Project(AuditBase):
    slug: Mapped[str] = m_col(unique=True)
    name: Mapped[str]
    description: Mapped[str]
    start_date: Mapped[datetime] = m_col(default=datetime.now)
    end_date: Mapped[datetime] = m_col(default=datetime.now)


class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class Service(service.Service[Project]):
    repository_type = Project


WriteDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"id", "created", "updated", "tasks"})]]
ReadDTO = SQLAlchemyDTO[Project]
