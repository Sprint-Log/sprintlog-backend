import logging
from typing import Any
from uuid import UUID

import httpx

from app.domain.backlogs.models import Backlog
from app.domain.projects.models import Project
from app.lib.plugin import BacklogPlugin, ProjectPlugin
from app.lib.settings import server

__all__ = ["ZulipBacklogPlugin"]
logger = logging.getLogger(__name__)


def log_info(message: str) -> None:
    return logger.info(message)


def send_msg_to_zulip(title: str, description: str) -> dict[str:str]:
    url: str = server.ZULIP_API_URL+server.ZULIP_SEND_MESSAGE_URL
    auth: str = (server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    log_info(url)
    data: dict[str:str] = {
        "type": "stream",
        "to": server.ZULIP_STREAM_NAME,
        "topic": title,
        "content": description
    }

    response = httpx.post(url, auth=auth, data=data)
    return response.json()

class ZulipBacklogPlugin(BacklogPlugin):
    def __init__(self, zulip_bot: str = "pipo") -> None:
        self.zulip_bot: str = zulip_bot
        return

    async def before_create(self, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        log_info(self.zulip_bot)
        if isinstance(data, Backlog):
            data.plugin_meta = {"zulip_bot": self.zulip_bot}
        elif isinstance(data, dict):
            data["plugin_meta"] = {"zulip_bot": self.zulip_bot}
        response = send_msg_to_zulip(data.title, data.description)
        if response["result"] != "success":
            log_info(response)
        else:
            log_info("successfully sent message to zulip")
        return data

    async def after_create(self, data: "Backlog") -> "Backlog":
        log_info(self.zulip_bot)
        return data

    async def before_update(self, item_id: str, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        return await super().before_update(item_id, data)

    async def after_update(self, data: "Backlog") -> "Backlog":
        return await super().after_update(data)

    async def before_delete(self, item_id: UUID) -> "UUID":
        log_info(self.zulip_bot)

        return item_id

    async def after_delete(self, data: "Backlog") -> "Backlog":
        log_info(self.zulip_bot)

        return data


class ZulipProjectPlugin(ProjectPlugin):
    def __init__(self, zulip_bot: str = "pipo") -> None:
        self.zulip_bot: str = zulip_bot
        return

    async def before_create(self, data: "Project | dict[str, Any]") -> "Project | dict[str, Any]":
        log_info(self.zulip_bot)
        if isinstance(data, Project):
            data.plugin_meta = {"zulip_bot": self.zulip_bot}
        elif isinstance(data, dict):
            data["plugin_meta"] = {"zulip_bot": self.zulip_bot}
            data["plugin_meta"] = {"zulip_object": self.zulip_bot}
        return data

    async def after_create(self, data: "Project") -> "Project":
        log_info(self.zulip_bot)
        return data

    async def before_update(self, item_id: str, data: "Project | dict[str, Any]") -> "Project | dict[str, Any]":
        return await super().before_update(item_id, data)

    async def after_update(self, data: "Project") -> "Project":
        return await super().after_update(data)

    async def before_delete(self, item_id: UUID) -> "UUID":
        log_info(self.zulip_bot)

        return item_id

    async def after_delete(self, data: "Project") -> "Project":
        log_info(self.zulip_bot)

        return data
