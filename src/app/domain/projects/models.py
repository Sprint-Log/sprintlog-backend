from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Annotated, Any

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig
from sqlalchemy import ARRAY, String
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
    pin: Mapped[bool] = m_col(default=False, server_default="false")
    labels: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    documents: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    start_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    backlogs: Mapped[list["Backlog"]] = relationship("Backlog", back_populates="project", lazy="noload")

    def __init__(self, **kw: Any):
        super().__init__(**kw)


class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class Service(SQLAlchemyAsyncRepositoryService[Project]):
    repository_type = Repository


WriteDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"id", "created", "updated", "backlogs"})]]
ReadDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"backlogs"})]]
