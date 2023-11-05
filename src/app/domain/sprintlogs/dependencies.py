"""User Account Controllers."""
from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.plugins
from app.domain.sprintlogs.models import SprintLog, SprintlogService
from app.lib import log
from app.lib.plugin import SprintlogPlugin
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
) -> AsyncGenerator[SprintlogService, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules([app.plugins.__path__[0]]):
        if name not in plugin.ENABLED:
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, SprintlogPlugin) and obj is not SprintlogPlugin:
                plugins.append(obj())
    async with SprintlogService.new(
        session=db_session,
        statement=select(SprintLog).order_by(SprintLog.updated_at.desc()).options(joinedload(SprintLog.project)),
    ) as service:
        service.plugins = set(plugins)
        try:
            yield service
        finally:
            ...
