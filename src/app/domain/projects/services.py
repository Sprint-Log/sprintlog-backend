from __future__ import annotations

from typing import Any
import re
import unicodedata
from structlog import getLogger
from litestar.exceptions import NotFoundException

from advanced_alchemy.repository import (
    SQLAlchemyAsyncSlugRepository,
)
from advanced_alchemy.service import (
    ModelDictT,
    SQLAlchemyAsyncRepositoryService,
)

from sqlalchemy import select
from app.lib.plugin import ProjectPlugin
from app.db import models as m

__all__ = ["ProjectService"]

logger = getLogger()


class ProjectService(SQLAlchemyAsyncRepositoryService[m.Project]):
    """Handles database operations for projects."""

    class ProjectRepository(SQLAlchemyAsyncSlugRepository[m.Project]):
        """Project SQLAlchemy Repository."""

        slug_field = "slug"
        model_type = m.Project

    repository_type = ProjectRepository

    plugins: set[ProjectPlugin] = set()

    def __init__(self, **repo_kwargs: Any) -> None:

        super().__init__(**repo_kwargs)

        self.model_type = self.repository.model_type

    async def get_project_assignees(self, slug: str) -> tuple[list[m.User], int]:
        project = await self.repository.get_by_slug(slug)
        if not project:
            raise NotFoundException("Project not found")

        team_ids = [team.id for team in project.teams]

        stmt = select(m.TeamMember).where(m.TeamMember.team_id.in_(team_ids))

        result = await self.repository.session.execute(stmt)
        team_members = result.scalars().all()
        users = [member.user for member in team_members if member.user]

        return users, len(users)

    async def create(
        self,
        data: ModelDictT[m.Project] | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        error_messages: dict[str, str] | None = None,
    ) -> m.Project:
        # Call the before_create hook for each registered plugin
        if not isinstance(data, dict):
            data = data.to_dict()

        name = data["name"]
        slug = self._slugify(name)

        is_unique = await self._is_slug_unique(slug=slug)
        if not is_unique:
            raise ValueError("Slug is not unique")
        logger.info(f"slug: {slug}")
        logger.info(f"is unique: {is_unique}")
        data["slug"] = slug

        data = await super().to_model(data, "create")
        self.repository.session

        for plugin in self.plugins:
            data = await plugin.before_create(data=data)

        if len(self.plugins) == 0:
            data.plugin_meta = {}

        obj: m.Project = await super().create(data)

        # Call the after_create hook for each registered plugin
        for plugin in self.plugins:
            await plugin.after_create(data=obj)

        return obj

    async def update(
        self,
        data: ModelDictT[m.Project],
        item_id: Any = None,
    ) -> m.Project:
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

    async def delete(
        self,
        item_id: Any,
    ) -> m.Project:

        for plugin in self.plugins:
            await plugin.before_delete(item_id=item_id)

        obj: m.Project = await super().delete(item_id=item_id)

        for plugin in self.plugins:
            await plugin.after_delete(data=obj)

        return obj

    def _slugify(self, value: str) -> str:
        """slugify.
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.

        Args:
            value (str): the string to slugify
        Returns:
            str: a slugified string of the value parameter
        """

        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

        value = re.sub(r"[^\w\s-]", "", value.lower())

        return re.sub(r"[-\s]+", "_", value).strip("-_")

    async def _is_slug_unique(
        self,
        slug: str,
        **kwargs: Any,
    ) -> bool:

        return await self.get_one_or_none(slug=slug) is None
