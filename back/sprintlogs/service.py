from __future__ import annotations

import secrets
from datetime import date, timedelta
from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, ModelDictT
from app.lib.plugin import SprintlogPlugin
from typing import Any
from app.db.models.sprintLog import SprintLog


class SprintLogService(SQLAlchemyAsyncRepositoryService[SprintLog]):
    """Handles database operations for projects."""

    class SprintLogRepository(SQLAlchemyAsyncSlugRepository[SprintLog]):
        """Project SQLAlchemy Repository."""

        model_type = SprintLog

        async def get_available_sprintlog_slug(self, sprintlog: SprintLog) -> str | None:
            project_slug: str = sprintlog.project_slug
            if not sprintlog.slug:
                token = secrets.token_hex(2)
                slug = f"{project_slug}-S{sprintlog.sprint_number}-{token}"
                if await self._is_slug_unique(slug):
                    return slug
            return sprintlog.slug

        async def _get_due_date(self, beg_date: date, est_days: float = 3.0) -> date:
            return beg_date + timedelta(days=est_days)

    repository_type = SprintLogRepository
    plugins: set[SprintlogPlugin] = set()

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: SprintLogService.SprintLogRepository = self.repository_type(**repo_kwargs)
        self.model_type = self.repository.model_type

        super().__init__(**repo_kwargs)

    async def to_model(
        self,
        data: ModelDictT[SprintLog] | dict[str, Any],
        operation: str | None = None,
    ) -> SprintLog:
        if isinstance(data, SprintLog):
            if operation == "create":
                slug = await self.repository.get_available_sprintlog_slug(sprintlog=data)
                data.slug = slug if slug else ""
            if not data.due_date:
                data.due_date = await self.repository._get_due_date(
                    data.beg_date,
                    data.est_days,
                )

        return await super().to_model(data, operation)

    async def create(self, data: ModelDictT[SprintLog] | dict[str, Any]) -> SprintLog:
        # Call the before_create hook for each registered plugin
        data = await self.to_model(data, "create")
        for plugin in self.plugins:
            data = await plugin.before_create(data=data)

        if len(self.plugins) == 0:
            data.plugin_meta = {}

        obj = await super().create(data)
        # Call the after_create hook for each
        for plugin in self.plugins:
            after = await plugin.after_create(data=obj)
            obj = await super().update(item_id=obj.id, data=after)

        return obj

    async def update(
        self,
        data: SprintLog | dict[str, Any],
        item_id: Any | None = None,
        old_data: SprintLog | dict | None = None,
    ) -> SprintLog:
        # Call the before_update hook for each registered plugin        if isinstance(data,SprintLog):
        data = await self.to_model(data, "update")
        for plugin in self.plugins:
            data = await plugin.before_update(
                item_id=item_id,
                data=data,
                old_data=old_data,
            )

        obj = await super().update(item_id=item_id, data=data)

        # Call the after_update hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_update(data=obj, old_data=old_data)

        return obj

    async def delete(
        self,
        item_id: Any,
    ) -> SprintLog:
        # Call the before_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj = await self.repository.delete(item_id)

        # Call the after_delete hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj
