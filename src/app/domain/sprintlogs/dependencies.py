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
from app.lib.settings import plugin

__all__ = ["provides_service"]


logger = log.get_logger()


def log_info(message: str) -> None:
    logger.info(message)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


async def provides_service(db_session: AsyncSession) -> AsyncGenerator[Service, None]:
    plugins = []
    for _, name, _ in pkgutil.iter_modules([app.plugins.__path__[0]]):
        if "zulip" not in plugin.PLUGINS and name == "zulip":
            log_info("skipped zulip plugin in sprintlog")
            continue
        module = __import__(f"{app.plugins.__name__}.{name}", fromlist=["*"])
        log_info(f"sprintlog module name: {module}")
        for obj_name in dir(module):
            log_info(f"sprintlog object name: {obj_name}")
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
