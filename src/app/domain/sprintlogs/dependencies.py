"""Sprintlog Service Provider."""

from __future__ import annotations

from typing import TYPE_CHECKING
import pkgutil

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.plugins
from app.config.base import get_settings
from app.lib.deps import create_service_provider
from app.lib.plugin import SprintlogPlugin
from app.domain.sprintlogs.service import SprintLogService
from app.db import models as m

if TYPE_CHECKING:
    from typing import Set
    from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()

__all__ = ("provide_sprintlog_service",)


def load_plugins() -> Set[SprintlogPlugin]:
    """Scan and load all enabled SprintlogPlugins from app.plugins."""
    found_plugins = set()
    for _, name, _ in pkgutil.iter_modules(list(app.plugins.__path__)):
        if name not in settings.plugin.ENABLED:
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, SprintlogPlugin) and obj is not SprintlogPlugin:
                found_plugins.add(obj())
    return found_plugins


PLUGINS = load_plugins()


class ExtendedSprintlogService(SprintLogService):
    """SprintlogService subclass that automatically loads plugins and sets statement."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            statement=select(m.SprintLog)
            .order_by(m.SprintLog.updated_at.desc())
            .options(joinedload(m.SprintLog.project)),
        )
        # Attach the pre-loaded plugins
        self.plugins = PLUGINS


provide_sprintlog_service = create_service_provider(
    ExtendedSprintlogService,
    load=[],
    error_messages={
        "duplicate_key": "This sprintlog item already exists.",
        "integrity": "Sprintlog operation failed.",
    },
)
