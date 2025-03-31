"""Sprintlog Service Provider."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator
import pkgutil

from sqlalchemy import select, case
from sqlalchemy.orm import joinedload

import app.plugins
from app.config.base import get_settings
from app.lib.plugin import SprintlogPlugin
from app.domain.sprintlogs.service import SprintLogService
from app.db import models as m
from structlog import get_logger
from app.db.models.enums import Priority

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


__all__ = ("provide_sprintlog_service",)

settings = get_settings()
logger = get_logger()


priority_order = case(
    (m.SprintLog.priority == Priority.hi, 3),
    (m.SprintLog.priority == Priority.med, 2),
    (m.SprintLog.priority == Priority.low, 1),
    else_=0,
)


async def provide_sprintlog_service(
    db_session: AsyncSession,
) -> AsyncGenerator[SprintLogService, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules(list(app.plugins.__path__)):
        if name not in settings.plugin.ENABLED:
            logger.info(f"skipped {name} plugin in sprintlog")
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, SprintlogPlugin) and obj is not SprintlogPlugin:
                plugins.append(obj())
    async with SprintLogService.new(
        session=db_session,
        statement=select(m.SprintLog)
        .order_by(priority_order.desc(), m.SprintLog.created_at.desc())
        .options(joinedload(m.SprintLog.project)),
    ) as service:
        service.plugins = set(plugins)
        try:
            yield service
        finally:
            ...
