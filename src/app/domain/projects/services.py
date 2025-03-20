
from __future__ import annotations

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import (
    ModelDictT,
    SQLAlchemyAsyncRepositoryService,
)
 
from app.lib.plugin import ProjectPlugin
from typing import Any, override
from app.db.models import Project

class ProjectService(SQLAlchemyAsyncRepositoryService[Project]):
    """Handles database operations for projects."""

    class ProjectRepository(SQLAlchemyAsyncSlugRepository[Project]):
        """Project SQLAlchemy Repository."""

        model_type = Project
        
    repository_type = ProjectRepository
    plugins: set[ProjectPlugin] = set()
    
    
    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: ProjectService.ProjectRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)

    async def create(
        self,
        data: ModelDictT[Project] | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        error_messages: dict[str, str] | None = None,
    ) -> Project:
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
        data: ModelDictT[Project],
        item_id: Any = None,
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

        obj = await super().update(
            item_id=item_id,
            data=data,
        )

        # Call the after_update hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_update(data=obj)

        return obj
    
    @override
    async def delete(
        self,
        item_id: Any,
    ) -> Project:
        # Call the before_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj: Project = await super().delete(item_id=item_id)

        # Call the after_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj
