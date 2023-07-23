from datetime import UTC, date, datetime
from typing import Annotated, Any
from uuid import UUID

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

from app.domain.accounts.models import User
from app.lib.db import orm
from app.lib.plugin import ProjectPlugin
from app.lib.service.sqlalchemy import SQLAlchemyAsyncRepositoryService

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
    pin: Mapped[bool] = m_col(default=False)
    labels: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    documents: Mapped[list[str]] = m_col(ARRAY(String), nullable=True)
    start_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    end_date: Mapped[date] = m_col(default=datetime.now(tz=UTC).date())
    sprint_weeks: Mapped[int | None] = m_col(default=2)
    sprint_amount: Mapped[int | None] = m_col(default=3)
    sprint_checkup_day: Mapped[int | None] = m_col(default=1)
    repo_urls: Mapped[list[str]] = m_col(ARRAY(String))
    plugin_meta: Mapped[dict] = m_col(default=lambda: dict, info=dto_field(Mark.READ_ONLY))  # Relationships
    owner_id: Mapped[UUID | None] = m_col(ForeignKey(User.id), nullable=True)
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )

    def __init__(self, **kw: Any):
        super().__init__(**kw)


class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class Service(SQLAlchemyAsyncRepositoryService[Project]):
    repository_type = Repository
    plugins: set[ProjectPlugin] = set()

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: Repository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)

    async def create(self, data: Project | dict[str, Any]) -> Project:
        # Call the before_create hook for each registered plugin
        for plugin in self.plugins:
            data = await plugin.before_create(data=data)
        obj: Project = await super().create(data)

        # Call the after_create hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_create(data=obj)

        return obj

    async def update(self, item_id: Any, data: Project | dict[str, Any]) -> Project:
        # Call the before_update hook for each registered plugin
        for plugin in self.plugins:
            data = await plugin.before_update(item_id=item_id, data=data)

        obj: Project = await super().update(item_id, data)

        # Call the after_update hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_update(data=obj)

        return obj

    async def delete(self, item_id: Any) -> Project:
        # Call the before_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj: Project = await super().delete(item_id)

        # Call the after_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj


WriteDTO = SQLAlchemyDTO[
    Annotated[Project, DTOConfig(exclude={"id", "created_at", "updated_at", "sprintlogs", "plugin_meta", "owner"})]
]
ReadDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"sprintlogs"})]]
