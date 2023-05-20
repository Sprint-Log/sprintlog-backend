from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Annotated

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import ARRAY
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.lib.db import orm
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

if TYPE_CHECKING:
    from app.domain.backlogs.models import Backlog

__all__ = [
    "Project",
    "ReadDTO",
    "Repository",
    "Service",
    "WriteDTO",
]


class Project(orm.TimestampedDatabaseModel):
    slug: Mapped[str] = m_col(unique=True)
    name: Mapped[str]
    description: Mapped[str]
    documents: Mapped[list[str]] = m_col(ARRAY, nullable=True)
    start_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    backlogs: Mapped[list["Backlog"]] = relationship("Backlog", back_populates="project", lazy="noload")


class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class Service(SQLAlchemyAsyncRepositoryService[Project]):
    repository_type = Repository


WriteDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"id", "created", "updated", "backlogs"})]]
ReadDTO = SQLAlchemyDTO[Project]
