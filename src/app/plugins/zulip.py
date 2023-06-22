import logging
from typing import Any
from uuid import UUID

import httpx
from httpx import BasicAuth

from app.domain.backlogs.models import Backlog
from app.domain.projects.models import Project
from app.lib.plugin import BacklogPlugin, ProjectPlugin
from app.lib.settings import server

__all__ = ["ZulipBacklogPlugin"]
logger = logging.getLogger(__name__)


def log_info(message: str) -> None:
    return logger.info(message)


async def send_msg(backlog_data: "Backlog | dict[str, Any]") -> dict[str, str]:
    log_info("sending message to zulip")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_SEND_MESSAGE_URL}"
    auth: BasicAuth = BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    log_info(url)

    content: str
    topic: str
    if isinstance(backlog_data, Backlog):
        content = f"{backlog_data.status} {backlog_data.priority} {backlog_data.progress} **[{backlog_data.slug}]** {backlog_data.title}  **:time::{backlog_data.due_date.strftime('%d-%m-%Y')}** @**{backlog_data.assignee_name}** {backlog_data.category}"
        topic = backlog_data.title
    elif isinstance(backlog_data, dict):
        content = f"{backlog_data['status']} {backlog_data['priority']} {backlog_data['progress']} **[{backlog_data['slug']}]** {backlog_data['title']}  **:time::{backlog_data['due_date'].strftime('%d-%m-%Y')}** @**{backlog_data['assignee_name']}** {backlog_data['category']}"
        topic = backlog_data["title"]
    log_info(content)
    data: dict[str, str] = {"type": "stream", "to": server.ZULIP_STREAM_NAME, "topic": topic, "content": content}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, auth=auth, data=data)
        return dict(response.json())


async def update_message(msg_id: int, topic: str, content: str) -> dict[str, str]:
    log_info("updaing message")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_SEND_MESSAGE_URL}{msg_id}"
    auth: BasicAuth = BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)

    data = {
        "topic": topic,
        "propagate_mode": "change_all",
        "send_notification_to_old_thread": "true",
        "send_notification_to_new_thread": "true",
        "content": content,
    }

    async with httpx.AsyncClient() as client:
        response = await client.patch(url, auth=auth, data=data)
        return dict(response.json())


async def create_stream(title: str, description: str, principals: list[str]) -> dict[str, str]:
    log_info("creating zulip stream")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_SEND_MESSAGE_URL}"
    auth: BasicAuth = BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            auth=auth,
            data={"subscriptions": [{"description": description, "name": title}], "principals": principals},
        )
        return dict(response.json())


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
        return data

    async def after_create(self, data: "Backlog") -> "Backlog":
        log_info(self.zulip_bot)
        try:
            response = await send_msg(data)
            if response["result"] != "success":
                log_info(str(response))
            else:
                log_info("successfully sent message to zulip")
                plugin_meta: dict[str, str] = data.plugin_meta
                plugin_meta["msg_id"] = response["id"]

                # TODO update msg id into database

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
            log_info(f"failed to send message to zulip: {e!s}")
        return data

    async def before_update(self, item_id: str, data: "Backlog | dict[str, Any]") -> "Backlog | dict[str, Any]":
        return await super().before_update(item_id, data)

    async def after_update(self, data: "Backlog") -> "Backlog":
        # TODO Call update_message function
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
        try:
            principals: list[str] = server.ZULIP_ADMIN_EMAIL
            name: str
            name = "" if data.owner.name is None else data.owner.name
            principals.append(name)
            log_info(str(principals))
            response = await create_stream(data.name, data.description, principals)
            if response["result"] != "success":
                log_info(str(response))
            else:
                log_info("successfully created zulip stream")
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
            log_info(f"failed to create zulip stream: {e!s}")
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
