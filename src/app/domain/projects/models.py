from collections.abc import Iterable
from typing import Annotated, Any

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy.orm import InstrumentedAttribute

from app.lib import log
from app.lib.plugin import ProjectPlugin
from app.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = [
    "Project",
    "ReadDTO",
    "Repository",
    "ProjectService",
    "WriteDTO",
]

logger = log.get_logger()


def log_info(message: str) -> None:
    logger.info(message)




class Repository(SQLAlchemyAsyncRepository[Project]):
    model_type = Project


class ProjectService(SQLAlchemyAsyncRepositoryService[Project]):
    repository_type = Repository
    plugins: set[ProjectPlugin] = set()

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: Repository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)

    async def create(self, data: Project | dict[str, Any]) -> Project:
        # Call the before_create hook for each registered plugin
        data = await super().to_model(data, "create")

        for plugin in self.plugins:
            data = await plugin.before_create(data=data)

        if len(self.plugins) == 0:
            data.plugin_meta = {}

        obj: Project = await super().create(data)

        # Call the after_create hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_create(data=obj)

        return obj

    async def update(
        self,
        data: Project | dict[str, Any],
        item_id: Any = None,
        attribute_names: Iterable[str] | None = None,
        with_for_update: bool | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        id_attribute: str | InstrumentedAttribute | None = None,
    ) -> Project:
        # Call the before_update hook for each registered plugin
        old_data = await self.repository.get(item_id)
        data = await super().to_model(data, "update")

        for plugin in self.plugins:
            data = await plugin.before_update(
                item_id=item_id,
                data=data,
                old_data=old_data,
            )

        obj = await super().update(item_id=item_id, data=data)

        # Call the after_update hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_update(data=obj)

        return obj

    async def delete(
        self,
        item_id: Any,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        id_attribute: str | InstrumentedAttribute | None = None,
    ) -> Project:
        # Call the before_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj: Project = await super().delete(item_id=item_id)

        # Call the after_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj


WriteDTO = SQLAlchemyDTO[
    Annotated[
        Project,
        DTOConfig(
            exclude={
                "id",
                "created_at",
                "updated_at",
                "sprintlogs",
                "plugin_meta",
                "owner",
            },
        ),
    ]
]
ReadDTO = SQLAlchemyDTO[Annotated[Project, DTOConfig(exclude={"sprintlogs"})]]
