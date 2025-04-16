from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any, Annotated
from litestar import Controller, get, post
from litestar.di import Provide
from litestar.params import Body
from litestar.channels import ChannelsPlugin
from litestar.response import ServerSentEvent

from app.domain.chat.schemas import Chat, ChatCreate
from app.domain.chat.deps import provide_chat_service

from app.domain.chat.service import ChatService
from uuid import UUID
from structlog import getLogger

logger = getLogger()


class StreamController(Controller):
    path = "/api/stream"
    tags = ["Chats"]

    dependencies = {"chat_service": Provide(provide_chat_service)}

    @get("/events/{topic:str}")
    async def get_notified(self, topic: str, channels: ChannelsPlugin) -> ServerSentEvent:
        async def generator() -> AsyncGenerator[bytes, Any]:
            async with channels.start_subscription([topic]) as subscriber:
                await channels.put_subscriber_history(subscriber, [topic], limit=100)
                async for event in subscriber.iter_events():
                    yield event

        return ServerSentEvent(generator(), event_type="stream")

    @post("/notify/{topic:str}")
    async def notify(self, topic: str, data: dict, channels: ChannelsPlugin, chat_service: ChatService) -> None:

        channels.publish(json.dumps(data), [topic])

    @post("/chats/create")
    async def create_message(self, data: Annotated[ChatCreate, Body()], chat_service: ChatService) -> Chat:
        chat = await chat_service.create(data=data)

        return chat_service.to_schema(data=chat, schema_type=Chat)

    @get("/chats/list/{sprint_id:uuid}")
    async def get_messages(self, sprint_id: UUID, chat_service: ChatService) -> list[Chat]:

        chats, total = await chat_service.list_and_count(sprint_id=sprint_id, parent_id=None)
        formatted_chats = []
        for chat in chats:
            formatted_chats.append(chat_service.to_chat_schema(chat))

        return formatted_chats
