"""User Account Controllers."""
from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING

import app.plugins
from app.domain.projects.models import ProjectService
from app.lib import log
from app.lib.plugin import ProjectPlugin
from app.lib.settings import plugin

__all__ = ["provides_service"]


logger = log.get_logger()


def log_info(message: str) -> None:
    logger.info(message)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProjectService, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules([app.plugins.__path__[0]]):
        if "zulip" not in plugin.ENABLED:
            log_info("skipped zulip plugin in project")
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        log_info(f"module name: {module}")
        for obj_name in dir(module):
            log_info(f"object name :{obj_name}")
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
