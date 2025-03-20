"""User Account Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from structlog import get_logger
import pkgutil
import app.plugins
from app.domain.projects.models import ProjectService
 
from app.lib.plugin import ProjectPlugin
from app.config.base import get_settings

settings = get_settings()

__all__ = ["provides_service"]


logger = get_logger()


def log_info(message: str) -> None:
    logger.info(message)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProjectService, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules(list(app.plugins.__path__)):
        log_info(f"checking plugin {name}")
        if name not in settings.plugin.ENABLED:
            log_info(f"skipped {name} plugin in sprintlog")
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        log_info(f"module name: {module}")
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
