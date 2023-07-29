import json
import logging
from typing import Any
from uuid import UUID

import httpx

from app.domain.projects.models import Project
from app.domain.sprintlogs.models import SprintLog
from app.lib.plugin import ProjectPlugin, SprintlogPlugin
from app.lib.settings import server

__all__ = ["ZulipSprintlogPlugin"]
logger = logging.getLogger(__name__)
backlog_topic: str = "📑 [BACKLOG] "


def log_info(message: str) -> None:
    return logger.info(message)


async def send_msg(stream_name: str, topic_name: str, content: str) -> Any:
    log_info("sending message to zulip")
    log_info(f"stream name: {stream_name}")
    log_info(f"topic name: {topic_name}")
    log_info(f"content: {content}")
    url = f"{server.ZULIP_API_URL}{server.ZULIP_SEND_MESSAGE_URL}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    log_info(url)
    data = {
        "type": "stream",
        "to": stream_name,
        "topic": topic_name,
        "content": content,
    }
    async with httpx.AsyncClient(timeout=1) as client:
        response = await client.post(url, auth=auth, data=data)
        if response.status_code == 200:
            return dict(response.json())
        raise httpx.HTTPError(f"{response.status_code}, {response.text}")


async def delete_message(msg_id: int) -> dict[str, Any]:
    log_info("deleting message")
    log_info(f"message id: {msg_id}")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_DELETE_MESSAGE_URL}/{msg_id}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    async with httpx.AsyncClient(timeout=1) as client:
        response = await client.delete(url, auth=auth)
        if response.status_code == 200:
            return dict(response.json())
        raise httpx.HTTPError(f"{response.status_code}, {response.text}")


async def update_message(msg_id: int, content: str) -> dict[str, Any]:
    log_info("updating message")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_UPDATE_MESSAGE_URL}/{msg_id}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    log_info(f"message id:{msg_id}")
    log_info(f"content :{content}")

    data = {
        "topic": backlog_topic,
        "propagate_mode": "change_one",
        "send_notification_to_old_thread": "true",
        "send_notification_to_new_thread": "true",
        "content": content,
    }

    async with httpx.AsyncClient(timeout=1) as client:
        response = await client.patch(url, auth=auth, data=data)
        if response.status_code == 200:
            return dict(response.json())
        raise httpx.HTTPError(f"{response.status_code}, {response.text}")


class ZulipSprintlogPlugin(SprintlogPlugin):
    def __init__(self, zulip_bot: str = "pipo") -> None:
        self.zulip_bot: str = zulip_bot
        return

    async def before_create(self, data: "SprintLog | dict[str, Any]") -> "SprintLog | dict[str, Any]":
        log_info(self.zulip_bot)
        if isinstance(data, SprintLog):
            data.plugin_meta = {"zulip_bot": self.zulip_bot}
        elif isinstance(data, dict):
            data["plugin_meta"] = {"zulip_bot": self.zulip_bot}
        return data

    async def after_create(self, data: "SprintLog") -> "SprintLog":
        log_info(self.zulip_bot)
        try:
            content: str
            stream_name: str
            if isinstance(data, SprintLog):
                content = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"
                stream_name = f"📌PRJ/{data.project_name}" if data.pin else f"PRJ/{data.project_name}"
            elif isinstance(data, dict):
                content = f"{data['status']} {data['priority']} {data['progress']} **[{data['slug']}]** {data['title']}  **:time::{data['due_date'].strftime('%d-%m-%Y')}** @**{data['assignee_name']}** {data['category']}"
                stream_name = f"📌PRJ/{data['project_name']}" if data.pin else f"PRJ/{data['project_name']}"
            response = await send_msg(stream_name, backlog_topic, content)
            if response["result"] != "success":
                log_info(f"failed to send message, response: {response}")
            else:
                log_info(f"successfully sent message to zulip {response['id']}")
                data.plugin_meta = {"msg_id": response["id"]}

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPError) as e:
            log_info(f"failed to send message to zulip: {e!s}")
        return data

    async def before_update(self, item_id: str, data: "SprintLog | dict[str, Any]") -> "SprintLog | dict[str, Any]":
        return await super().before_update(item_id, data)

    async def after_update(self, data: "SprintLog") -> "SprintLog":
        log_info(self.zulip_bot)
        data = await super().after_update(data)
        if data.type == "task":
            log_info("task type; updating backlog to task")
            # need to know if it's updating status or changing backlog to task
            try:
                task_msg_id: Any
                content: str
                stream_name: str
                topic_name: str
                description: str
                if isinstance(data, SprintLog):
                    description = data.description
                    content = f"**:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**"
                    stream_name = f"📌PRJ/{data.project_name}" if data.pin else f"PRJ/{data.project_name}"
                    topic_name = f"{data.status} {data.priority} {data.progress} [{data.slug}] {data.title} {data.category}"
                elif isinstance(data, dict):
                    description = data["description"]
                    content = f"**:time::{data['due_date'].strftime('%d-%m-%Y')}** @**{data['assignee_name']}**"
                    stream_name = f"📌PRJ/{data['project_name']}" if data.pin else f"PRJ/{data['project_name']}"
                    topic_name = f"{data['status']} {data['priority']} {data['progress']} [{data['slug']}] {data['title']} {data['category']}"
                if description != "":
                    log_info("backlog description is not empty. send description")
                    await send_msg(stream_name, topic_name, description)
                response = await send_msg(stream_name, topic_name, content)
                if response["result"] != "success":
                    log_info(f"failed to send message to zulip for task {response}")
                else:
                    log_info("successfully sent message to zulip for task")
                    task_msg_id = {"msg_id": response["id"]}

                # delete item from the backlog
                try:
                    msg_id = data.plugin_meta.get("msg_id")
                    if msg_id:
                        response: dict[str, Any] | None = await delete_message(msg_id=msg_id)
                        if response:
                            if response.get("result") != "success":
                                log_info(f"failed to delete message: {str(response)}")
                            else:
                                log_info(f"successfully deleted message from zulip {response}")
                except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPError) as e:
                    log_info(f"failed to send task message: {e!s}")

                if task_msg_id is not None:
                    data.plugin_meta = task_msg_id

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPError) as e:
                log_info(f"failed to send message to zulip: {e!s}")
        else:
            try:
                log_info("backlog type; updating message")
                msg_id = data.plugin_meta.get("msg_id")
                content: str = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"
                if msg_id:
                    response: dict[str, Any] | None = await update_message(msg_id=msg_id, content=content)
                    if response:
                        if response.get("result") != "success":
                            log_info(f"failed to update message to zulip {str(response)}")
                        else:
                            log_info(f"successfully update message to zulip {response}")
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPError) as e:
                log_info(f"failed to update message: {e!s}")
        return data

    async def before_delete(self, item_id: UUID) -> "UUID":
        log_info(self.zulip_bot)

        return item_id

    async def after_delete(self, data: "SprintLog") -> "SprintLog":
        log_info(self.zulip_bot)

        return data


async def create_stream(
    title: str,
    description: str,
    principals: list[str],
    is_pinned: bool | None = False,
) -> dict[str, str]:
    log_info("creating zulip stream")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_CREATE_STREAM_URL}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    tag = f"📌PRJ/{title}" if is_pinned else f"PRJ/{title}"
    subscription: list[dict[str, str]] = [{"description": description, "name": tag}]
    data = {
        "subscriptions": json.dumps(subscription),
        "principals": json.dumps(principals),
        "invite_only": True,
        "history_public_to_subscribers": True,
    }
    async with httpx.AsyncClient(timeout=1) as client:
        response = await client.post(url, auth=auth, data=data)
        log_info(str(response))
        if response.status_code == 200:
            return dict(response.json())
        raise httpx.HTTPError(f"{response.status_code}, {response.text}")


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
            email: str
            email = "" if data.owner.email is None else data.owner.email
            principals.append(server.ZULIP_EMAIL_ADDRESS)
            principals.append(email)
            log_info(str(principals))
            response = await create_stream(data.name, data.description, principals, data.pin)
            if response["result"] != "success":
                log_info(str(response))
            else:
                log_info("successfully created zulip stream")
        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.HTTPError) as e:
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
