import json
import logging
from enum import Enum
from typing import Any
from uuid import UUID

import httpx

from app.domain.projects.models import Project
from app.domain.sprintlogs.models import SprintLog
from app.lib import serialization
from app.lib.plugin import ProjectPlugin, SprintlogPlugin
from app.lib.settings import server

__all__ = ["ZulipSprintlogPlugin"]
logger = logging.getLogger(__name__)
backlog_topic = "📑 [BACKLOG] "


def log_info(message: str) -> None:
    return logger.exception(message)


class StatusFlags(Enum):
    BACKLOG_UPDATE = 1
    SPRINT_UPDATE = 2
    SWITCH_TO_BACKLOG = 4
    SWITCH_TO_TASK = 8


async def create_stream(
    name: str,
    description: str,
    principals: list[str],
) -> dict[str, str]:
    log_info("creating zulip stream")
    url = f"{server.ZULIP_API_URL}{server.ZULIP_CREATE_STREAM_URL}"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    subscription = [{"description": description, "name": name}]
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


def _gen_stream_name(name: str, is_pinned: bool | None = False) -> str:
    log_info(f">>> {name}")
    return f"📌PRJ/{name}" if is_pinned else f"PRJ/{name}"


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
        if response.status_code == 400 and dict(response.json()).get("code") == "STREAM_DOES_NOT_EXIST":
            await create_stream(
                stream_name,
                "Stream rebuild due to inexistance",
                principals=[*server.ZULIP_ADMIN_EMAIL, server.ZULIP_EMAIL_ADDRESS],
            )
            response = await client.post(url, auth=auth, data=data)
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


async def delete_topic(stream_id: int, topic: str) -> dict[str, Any]:
    url: str = f"{server.ZULIP_API_URL}/api/v1/streams/{stream_id}/delete_topic"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.post(url, auth=auth, data={"topic_name": topic})
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


async def get_stream_id(stream_name: str) -> dict[str, Any]:
    url: str = f"{server.ZULIP_API_URL}/api/v1/get_stream_id"
    auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)
    async with httpx.AsyncClient(timeout=1000) as client:
        response = await client.get(url, auth=auth, params={"stream": stream_name})
        log_info(response)
        if response.status_code == 200:
            return dict(response.json())
        msg = f"{response.status_code}, {response.text}"
        raise httpx.HTTPError(msg)


class ZulipSprintlogPlugin(SprintlogPlugin):
    status: StatusFlags

    def __init__(self) -> None:
        ...

    def _format_content(self, data: SprintLog) -> dict:
        stream_name = _gen_stream_name(data.project_name, data.pin)
        topic_name = f"{data.progress} {data.title} {data.category}  {data.priority} {data.status}"
        content = f"[{data.slug}] **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**\n{data.description}"
        return {
            "content": content,
            "stream_name": stream_name,
            "topic_name": topic_name,
        }

    async def _delete_zulip_item(
        self,
        existing_meta: dict,
        delete_mode: str,
        topic_name: str,
        stream_name: str,
    ) -> None:
        if delete_mode:
            match delete_mode:
                case "message":
                    current_msg_id = existing_meta.get("msg_id")
                    if current_msg_id:
                        try:
                            response = await delete_message(msg_id=current_msg_id)
                            if response and response.get("result") == "success":
                                log_info(f"successfully deleted message from zulip {response}")
                        except (
                            httpx.ConnectTimeout,
                            httpx.ReadTimeout,
                            httpx.ConnectError,
                            httpx.HTTPError,
                        ):
                            logger.exception("failed to delete message.")
                case "topic":
                    try:
                        stream_id_response = await get_stream_id(stream_name=stream_name)
                        stream_id = stream_id_response.get("stream_id")
                        response = await delete_topic(stream_id, topic_name)
                        if response and response.get("result") == "success":
                            log_info(f"successfully deleted topic from zulip {response}")
                    except (
                        httpx.ConnectTimeout,
                        httpx.ReadTimeout,
                        httpx.ConnectError,
                        httpx.HTTPError,
                    ):
                        logger.exception("failed to delete topic.")

    async def _update_message(
        self,
        topic_name: str,
        msg_id: int,
        content: str,
        propagate_mode: str,
        stream_name: str | None = None,
    ) -> dict[str, Any]:
        url = f"{server.ZULIP_API_URL}{server.ZULIP_UPDATE_MESSAGE_URL}/{msg_id}"
        auth = httpx.BasicAuth(server.ZULIP_EMAIL_ADDRESS, server.ZULIP_API_KEY)

        data = {
            "topic": topic_name,
            "propagate_mode": propagate_mode,
            "send_notification_to_new_thread": "false",
            "send_notification_to_old_thread": "false",
            "content": content,
        }

        async with httpx.AsyncClient(timeout=1000) as client:
            response = await client.patch(url, auth=auth, data=data)
            if response.status_code == 200:
                return dict(response.json())
            if (
                response.status_code == 400
                and dict(response.json()).get("code") == "BAD_REQUEST"
                and dict(response.json()).get("message") == "Invalid message(s)"
            ) and stream_name:
                await create_stream(
                    stream_name,
                    "Stream rebuild due to inexistance",
                    principals=[*server.ZULIP_ADMIN_EMAIL, server.ZULIP_EMAIL_ADDRESS],
                )
            msg = f"{response.status_code}, {response.text}"
            raise httpx.HTTPError(msg)

    async def _update_backlog(self, data: SprintLog, meta_data: dict) -> SprintLog:
        msg_id = meta_data.get("msg_id")
        content = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"
        if msg_id:
            response = await self._update_message(
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
                    response["id"] = msg_id

        return response

    async def _switch_topic(
        self,
        data: SprintLog,
        existing_meta: dict,
        switch_to: str,
        delete_mode: str | None = "message",
        project_name: str = "",
    ) -> SprintLog:
        log_info(f">>> mode {delete_mode}")
        if not data.project_name and project_name:
            content, _, topic_name = self._format_content(data).values()
            stream_name = _gen_stream_name(project_name)
        else:
            content, stream_name, topic_name = self._format_content(data).values()

        await self._delete_zulip_item(existing_meta, delete_mode, topic_name, stream_name)

        if switch_to == "task":
            msg_response = await send_msg(stream_name, topic_name, content)
        else:
            msg_response = await self._update_backlog(data, existing_meta)

        if msg_response["result"] == "success":
            new_meta = {
                "msg_id": msg_response["id"],
            }
            data.plugin_meta = new_meta

        return data

    async def _update_task_message(
        self,
        data: SprintLog,
        meta_data: dict,
        propagation: str = "change_all",
    ) -> SprintLog:
        msg_id = meta_data.get("msg_id")
        content, _stream_name, topic_name = self._format_content(data).values()
        if msg_id:
            response = await self._update_message(
                topic_name=topic_name,
                msg_id=msg_id,
                content=content,
                propagate_mode=propagation,
            )
            if response:
                if response.get("result") != "success":
                    log_info(f"failed to update message to zulip {response!s}")
                else:
                    log_info(f"successfully update message to zulip {response}")
        return data

    async def before_create(self, data: "SprintLog") -> "SprintLog":
        data.plugin_meta = None
        return data

    async def after_create(self, data: "SprintLog") -> "SprintLog":
        try:
            log_info(">>> after_create trigger")
            stream_name = _gen_stream_name(data.project_name, data.pin)
            content = f"{data.status} {data.priority} {data.progress} **[{data.slug}]** {data.title}  **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}** {data.category}"

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

    def _set_status(self, data: SprintLog, old_data: SprintLog) -> StatusFlags:
        backlogged = data.type == "backlog"
        switched = data.type != old_data.get("type") if isinstance(old_data, dict) else False
        if backlogged and not switched:
            self.status = StatusFlags.BACKLOG_UPDATE
            return self.status
        if not backlogged and not switched:
            self.status = StatusFlags.SPRINT_UPDATE
            return self.status
        if backlogged and switched:
            self.status = StatusFlags.SWITCH_TO_BACKLOG
            return self.status
        if not backlogged and switched:
            self.status = StatusFlags.SWITCH_TO_TASK
            return self.status
        return None

    async def before_update(
        self,
        item_id: str | None,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        data = await super().before_update(item_id, data)
        meta_data = (
            serialization.eval_from_b64(data.plugin_meta)
            if data.plugin_meta
            else serialization.eval_from_b64(old_data.plugin_meta)
        )
        status = self._set_status(data, old_data)
        project_name = old_data.project_name if isinstance(old_data, SprintLog) else data.project_name

        if meta_data:
            try:
                log_info(status)
                match self.status:
                    case StatusFlags.BACKLOG_UPDATE:
                        return await self._update_task_message(data, meta_data)
                    case StatusFlags.SPRINT_UPDATE:
                        return await self._update_task_message(data, meta_data)
                    case StatusFlags.SWITCH_TO_BACKLOG:
                        return await self._switch_topic(
                            data,
                            meta_data,
                            "backlog",
                            delete_mode="topic",
                            project_name=project_name,
                        )
                    case StatusFlags.SWITCH_TO_TASK:
                        return await self._switch_topic(
                            data,
                            meta_data,
                            "task",
                            delete_mode="message",
                            project_name=project_name,
                        )
            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.HTTPError,
            ):
                return data

        else:
            log_info(f">>>cant get meta: {meta_data}")
            await self._switch_topic(data, meta_data, "task", None, project_name)

        return data

    async def after_update(
        self,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        data = await super().after_update(data)
        log_info(f"metadata project {data.plugin_meta}")
        meta_data = serialization.eval_from_b64(data.plugin_meta)

        return data

    async def before_delete(self, item_id: UUID) -> "UUID":
        return item_id

    async def after_delete(self, data: "SprintLog") -> "SprintLog":
        return data


class ZulipProjectPlugin(ProjectPlugin):
    def __init__(self) -> None:
        ...

    async def before_create(self, data: "Project") -> "Project":
        return data

    async def after_create(self, data: "Project") -> "Project":
        try:
            email = "" if data.owner.email is None else data.owner.email
            principals = [*server.ZULIP_ADMIN_EMAIL, server.ZULIP_EMAIL_ADDRESS, email]
            stream_name = _gen_stream_name(data.name, data.pin)

            response = await create_stream(stream_name, data.description, principals)
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

    async def before_update(
        self,
        item_id: UUID,
        data: Project,
        old_data: Project | None = None,
    ) -> "Project":
        return await super().before_update(item_id, data, old_data)

    async def after_update(self, data: "Project") -> "Project":
        return await super().after_update(data)

    async def before_delete(self, item_id: UUID) -> "UUID":
        return item_id

    async def after_delete(self, data: "Project") -> "Project":
        return data
