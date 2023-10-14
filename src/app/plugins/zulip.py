import json
import logging
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
                server.ZULIP_ADMIN_EMAIL,
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


class ZulipSprintlogPlugin(SprintlogPlugin):
    def __init__(self) -> None:
        ...

    def _format_content(self, data: SprintLog) -> dict:
        stream_name = _gen_stream_name(data.project_name, data.pin)

        topic_name = f"{data.progress} {data.title} {data.category}  {data.priority} {data.status}"

        content = f"""{data.description}
        [{data.slug}] **:time::{data.due_date.strftime('%d-%m-%Y')}** @**{data.assignee_name}**
        f"""
        return {
            "content": content,
            "stream_name": stream_name,
            "topic_name": topic_name,
        }

    async def _move_zulip_task(
        self,
        data: SprintLog,
        existing_meta: dict,
        delete_msg: bool,
    ) -> SprintLog:
        if delete_msg:
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
                    logger.exception("failed to send message to zulip:")

        content, stream_name, topic_name = self._format_content(data).values()
        msg_response = await send_msg(stream_name, topic_name, content)
        if msg_response["result"] == "success":
            new_meta = {
                "msg_id": msg_response["id"],
                "task": True,
                topic_name: topic_name,
            }
            data.plugin_meta = new_meta

        return data

    async def _update_message(
        self,
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
            "send_notification_to_new_thread": "false",
            "send_notification_to_old_thread": "false",
            "content": content,
        }

        async with httpx.AsyncClient(timeout=1000) as client:
            response = await client.patch(url, auth=auth, data=data)
            if response.status_code == 200:
                return dict(response.json())
            msg = f"{response.status_code}, {response.text}"
            raise httpx.HTTPError(msg)

    async def _update_backlog(self, data: SprintLog, meta_data: dict) -> SprintLog:
        log_info("backlog type: updating message")
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
        return data

    async def _update_task(
        self,
        data: SprintLog,
        meta_data: dict,
        propagation: str = "change_all",
    ) -> SprintLog:
        log_info("backlog type: updating message")
        msg_id = meta_data.get("msg_id")
        content, stream_name, topic_name = self._format_content(data).values()
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

    async def before_update(
        self,
        item_id: str | None,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        meta_data = serialization.eval_from_b64(data.plugin_meta) if data.plugin_meta else None
        if meta_data:
            backlogged = data.type == "backlog"
            switched = data.type != old_data.get("type") if isinstance(old_data, dict) else False
            backlog_update = backlogged and not switched
            sprint_update = not backlogged and not switched
            switch_to_backlog = backlogged and switched
            switch_to_task = not backlogged and switched

            try:
                if backlog_update:
                    log_info("Just Backlog Update")
                    log_info(f"update_data {data.type}")
                    return await self._update_task(data, meta_data)
                if sprint_update:
                    log_info("Just Sprint Update")
                    log_info(f"update_data {data.type}")
                    return await self._update_task(data, meta_data)
                if switch_to_backlog:
                    log_info("Swithcing to bacjlog")
                    return await self._move_zulip_task(data, meta_data, True)
                if switch_to_task:
                    log_info("Swithcing to task")
                    return await self._move_zulip_task(data, meta_data, False)
            except (
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.ConnectError,
                httpx.HTTPError,
            ):
                return data

        else:
            log_info("cant get meta")
            await self._move_zulip_task(data, meta_data, False)

        return data

    async def after_update(
        self,
        data: "SprintLog",
        old_data: "SprintLog|dict|None" = None,
    ) -> "SprintLog":
        data = await super().after_update(data)
        log_info(f"metadata project {data.plugin_meta}")
        meta_data = serialization.eval_from_b64(data.plugin_meta)
        is_tasked = meta_data.get("task")
        if data.type != "task" or not is_tasked:
            try:
                data = await self._update_backlog(data, meta_data)
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
            response = await create_stream(data.name, data.description, principals)
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
