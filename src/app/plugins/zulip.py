import json
import logging
from typing import TYPE_CHECKING, Any
from uuid import UUID

import httpx

from app.lib import serialization

if TYPE_CHECKING:
    from app.domain.projects.models import Project

from app.domain.sprintlogs.models import SprintLog
from app.lib.plugin import ProjectPlugin, SprintlogPlugin
from app.lib.settings import server

__all__ = ["ZulipSprintlogPlugin"]
logger = logging.getLogger(__name__)
backlog_topic = "📑 [BACKLOG] "


def log_info(message: str) -> None:
    return logger.exception(message)


async def send_msg(stream_name: str, topic_name: str, content: str | None = "") -> dict:
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
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url, auth=auth, data=data)
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


async def delete_message(msg_id: int) -> dict[str, Any]:
    log_info("deleting message")
    log_info(f"message id: {msg_id}")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_DELETE_MESSAGE_URL}/{msg_id}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.delete(url, auth=auth)
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


async def update_message(
    topic_name: str,
    msg_id: int,
    content: str,
    propagate_mode: str,
) -> dict[str, Any]:
    log_info("updating message")
    url: str = f"{server.ZULIP_API_URL}{server.ZULIP_UPDATE_MESSAGE_URL}/{msg_id}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    log_info(f"message id:{msg_id}")
    log_info(f"content :{content}")

    data = {
        "topic": topic_name,
        "propagate_mode": propagate_mode,
        "send_notification_to_new_thread": "true",
        "content": content,
    }

    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.patch(url, auth=auth, data=data)
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


def format_content(data: SprintLog) -> dict:
    stream_name = f"📌PRJ/{data.project_name}" if data.pin else f"PRJ/{data.project_name}"

    topic_name = f"{data.progress} {data.title} {data.category}  {data.priority} {data.status}"

    content = f"""{data.description}
    [{data.slug}] **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**
    f"""
    return {"content": content, "stream_name": stream_name, "topic_name": topic_name}


async def update_backlog(data: SprintLog) -> dict:
    meta_data = serialization.eval_from_b64(data.plugin_meta)
    content, stream_name, topic_name = format_content(data).values()
    msg_response = await send_msg(stream_name, topic_name, content)
    if msg_response["result"] != "success":
        log_info(f"failed to send message to zulip for task {msg_response}")
    else:
        log_info("successfully sent message to zulip for task")
        task_msg_id = {
            "msg_id": msg_response["id"],
            "task": True,
            topic_name: topic_name,
        }
        data.plugin_meta = task_msg_id
    try:
        msg_id = meta_data.get("msg_id")
        if msg_id:
            response = await delete_message(msg_id=msg_id)
            if response and response.get("result") != "success":
                log_info(f"failed to delete message: {response!s}")
            else:
                log_info(f"successfully deleted message from zulip {response}")
    except (
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.ConnectError,
        httpx.HTTPError,
    ):
        logger.exception("failed to send message to zulip:")

    return msg_response


class ZulipSprintlogPlugin(SprintlogPlugin):
    def __init__(self) -> None:
        ...

    async def before_create(self, data: "SprintLog") -> "SprintLog":
        data.plugin_meta = {}
        return data

    async def after_create(self, data: "SprintLog") -> "SprintLog":
        try:
            content = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"
            stream_name = f"📌PRJ/{data.project_name}" if data.pin else f"PRJ/{data.project_name}"

            response = await send_msg(stream_name, backlog_topic, content)
            if response["result"] != "success":
                log_info(f"failed to send message, response: {response}")
            else:
                log_info(f"successfully sent message to zulip {response['id']}")
                data.plugin_meta = {"msg_id": response["id"]}

        except (
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.ConnectError,
            httpx.HTTPError,
        ):
            log_info("failed to send message to zulip: ")
        return data

    async def before_update(  # noqa: C901, PLR0915 , PLR0912
        self,
        item_id: str | None,
        data: "SprintLog",
    ) -> "SprintLog":
        data = await super().before_update(item_id, data)
        meta_data = serialization.eval_from_b64(data.plugin_meta)
        is_tasked = meta_data.get("task") if data.plugin_meta else False
        task_msg_id: dict | None = None
        if not is_tasked:
            if data.type == "task":
                log_info("task type: updating backlog to task before_update")
                # need to know if it's updating status or changing backlog to task
                try:
                    description = data.description
                    content = f"[{data.slug}] **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**"
                    stream_name = f"📌PRJ/{data.project_name}" if data.pin else f"PRJ/{data.project_name}"
                    topic_name = f"{data.progress} {data.title} {data.category} {data.status} {data.priority}"
                    if description != "":
                        log_info("backlog description is not empty. send description")
                        await send_msg(stream_name, topic_name, description)
                    msg_response = await send_msg(stream_name, topic_name, content)
                    if msg_response["result"] != "success":
                        log_info(
                            f"failed to send message to zulip for task {msg_response}",
                        )
                    else:
                        log_info("successfully sent message to zulip for task")
                        task_msg_id = {
                            "msg_id": msg_response["id"],
                            "task": True,
                            topic_name: topic_name,
                        }

                    # delete item from the backlog
                    try:
                        msg_id = meta_data.get("msg_id")
                        if msg_id:
                            response: dict[str, Any] | None = await delete_message(
                                msg_id=msg_id,
                            )
                            if response:
                                if response.get("result") != "success":
                                    log_info(f"failed to delete message: {response!s}")
                                else:
                                    log_info(
                                        f"successfully deleted message from zulip {response}",
                                    )
                    except (
                        httpx.ConnectTimeout,
                        httpx.ReadTimeout,
                        httpx.ConnectError,
                        httpx.HTTPError,
                    ):
                        log_info("failed to send task message: ")

                    if task_msg_id:
                        data.plugin_meta = task_msg_id

                except (
                    httpx.ConnectTimeout,
                    httpx.ReadTimeout,
                    httpx.ConnectError,
                    httpx.HTTPError,
                ):
                    logger.exception("failed to send message to zulip:")
            else:
                try:
                    log_info("task type: updating topic")
                    msg_id = meta_data.get("msg_id")
                    update_content: str = (
                        f"[{data.slug}] **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**"
                    )
                    topic_name = f"{data.progress} {data.title} {data.category} {data.status} {data.priority}"
                    if msg_id:
                        update_response = await update_message(
                            topic_name=topic_name,
                            msg_id=msg_id,
                            content=update_content,
                            propagate_mode="change_all",
                        )
                        if update_response:
                            if update_response.get("result") != "success":
                                log_info(
                                    f"failed to update message to zulip {update_response!s}",
                                )
                            else:
                                log_info(
                                    f"successfully update message to zulip {update_response}",
                                )
                                task_msg_id = {
                                    "msg_id": msg_id,
                                    "task": True,
                                    topic_name: topic_name,
                                }

                    if task_msg_id:
                        data.plugin_meta = task_msg_id

                except (
                    httpx.ConnectTimeout,
                    httpx.ReadTimeout,
                    httpx.ConnectError,
                    httpx.HTTPError,
                ):
                    log_info("failed to update message: ")
        return data

    async def after_update(self, data: "SprintLog") -> "SprintLog":
        data = await super().after_update(data)
        log_info(f"metadata project {data.plugin_meta}")
        meta_data = serialization.eval_from_b64(data.plugin_meta)
        is_tasked = meta_data.get("task")
        if data.type != "task" or not is_tasked:
            try:
                log_info("backlog type: updating message")
                msg_id = meta_data.get("msg_id")
                content = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"
                if msg_id:
                    response = await update_message(
                        topic_name=backlog_topic,
                        msg_id=msg_id,
                        content=content,
                        propagate_mode="change_one",
                    )
                    if response:
                        if response.get("result") != "success":
                            log_info(f"failed to update message to zulip {response!s}")
                        else:
                            log_info(f"successfully update message to zulip {response}")
            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.HTTPError,
            ):
                log_info("failed to update message: ")
        return data

    async def before_delete(self, item_id: UUID) -> "UUID":
        return item_id

    async def after_delete(self, data: "SprintLog") -> "SprintLog":
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
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url, auth=auth, data=data)
        log_info(str(response))
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


class ZulipProjectPlugin(ProjectPlugin):
    def __init__(self) -> None:
        ...

    async def before_create(self, data: "Project") -> "Project":
        return data

    async def after_create(self, data: "Project") -> "Project":
        try:
            principals: list[str] = server.ZULIP_ADMIN_EMAIL
            email: str
            email = "" if data.owner.email is None else data.owner.email
            principals.append(server.ZULIP_EMAIL_ADDRESS)
            principals.append(email)
            log_info(str(principals))
            response = await create_stream(
                data.name,
                data.description,
                principals,
                data.pin,
            )
            if response["result"] != "success":
                log_info(str(response))
            else:
                log_info("successfully created zulip stream")
        except (
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.ConnectError,
            httpx.HTTPError,
        ):
            log_info("failed to create zulip stream: ")
        return data

    async def before_update(self, item_id: UUID, data: "Project") -> "Project":
        return await super().before_update(item_id, data)

    async def after_update(self, data: "Project") -> "Project":
        return await super().after_update(data)

    async def before_delete(self, item_id: UUID) -> "UUID":
        return item_id

    async def after_delete(self, data: "Project") -> "Project":
        return data
