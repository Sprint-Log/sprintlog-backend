import pkgutil
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Annotated, Any
from uuid import UUID

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto.factory import DTOConfig, Mark, dto_field
from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column as m_col

import app.plugins
from app.domain.accounts.models import User
from app.lib.db import orm
from app.lib.plugin import ProjectPlugin
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
    sprint_weeks: Mapped[int | None] = m_col(default=2, server_default="2")
    sprint_amount: Mapped[int | None] = m_col(default=3, server_default="3")
    sprint_checkup_day: Mapped[int | None] = m_col(default=1, server_default="1")
    repo_urls: Mapped[list[str]] = m_col(ARRAY(String), server_default="[]")
    backlogs: Mapped[list["Backlog"]] = relationship("Backlog", back_populates="project", lazy="noload")
    plugin_meta: Mapped[dict[str, Any]] = m_col(JSONB, default={})
    owner_id: Mapped[UUID | None] = m_col(ForeignKey(User.id))
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        foreign_keys="Project.owner_id",
        lazy="joined",
        info=dto_field(Mark.PRIVATE),
    )

    def __init__(self, **kw: Any):
        super().__init__(**kw)


class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class Service(SQLAlchemyAsyncRepositoryService[Project]):
    repository_type = Repository
    plugins: list[ProjectPlugin] = []

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: Repository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)
        for _, name, _ in pkgutil.iter_modules([app.plugins.__path__[0]]):
            module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if isinstance(obj, type) and issubclass(obj, ProjectPlugin) and obj is not ProjectPlugin:
                    self.register_plugin(obj())

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

    def register_plugin(self, plugin: ProjectPlugin) -> None:
        self.plugins.append(plugin)


WriteDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"id", "created_at", "updated_at", "backlogs"})]]
ReadDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"backlogs"})]]
