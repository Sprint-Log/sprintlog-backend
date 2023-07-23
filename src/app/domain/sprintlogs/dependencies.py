"""User Account Controllers."""
from __future__ import annotations

import pkgutil
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.plugins
from app.domain.sprintlogs.models import Service, SprintLog
from app.lib import log
from app.lib.plugin import SprintlogPlugin

__all__ = ["provides_service"]


logger = log.get_logger()

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_service(db_session: AsyncSession) -> AsyncGenerator[Service, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules([app.plugins.__path__[0]]):
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        for obj_name in dir(module):
            obj = getattr(module, obj_name)
            if isinstance(obj, type) and issubclass(obj, SprintlogPlugin) and obj is not SprintlogPlugin:
                plugins.append(obj())
    async with Service.new(
        session=db_session,
        statement=select(SprintLog).order_by(SprintLog.due_date).options(joinedload(SprintLog.project)),
    ) as service:
        service.plugins = set(plugins)
        try:
            yield service
        finally:
            ...
