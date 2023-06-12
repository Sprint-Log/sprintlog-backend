import logging
from typing import TYPE_CHECKING, Any

from app.lib.plugin import BacklogPlugin

if TYPE_CHECKING:
    from app.domain.backlogs.models import Backlog

__all__ = ["ZulipBacklogPlugin"]
logger = logging.getLogger(__name__)


async def send_email(email_list: str, message: str) -> None:
    return logger.info(email_list, message)


class ZulipBacklogPlugin(BacklogPlugin):
    def __init__(self, email_list: str) -> None:
        self.email_list: str = email_list

    async def before_create(self, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        return data

    async def after_create(self, data: "Backlog") -> "Backlog":
        return await super().after_create(data)
