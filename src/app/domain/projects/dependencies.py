"""Project Service Provider."""

from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING
from structlog import get_logger
import app.plugins
from app.config.base import get_settings
from app.domain.projects.services import ProjectService
from app.lib.plugin import ProjectPlugin

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()
logger = get_logger()

__all__ = ("provide_project_service",)


async def provide_project_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProjectService, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules(list(app.plugins.__path__)):
        logger.info(f"checking plugin from project {name}")
        if name not in settings.plugin.ENABLED:
            logger.info(f"skipped {name} plugin in projects")
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        logger.info(f"module name: {module}")
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, ProjectPlugin) and obj is not ProjectPlugin:
                plugins.append(obj())
    """Construct repository and ProjectService objects for the request."""
    async with ProjectService.new(session=db_session) as service:
        service.plugins = set(plugins)
        try:
            yield service
        finally:
            ...
