from collections.abc import AsyncGenerator
from typing import Any, Sequence
from litestar import Controller, get, post
from litestar.di import Provide
from litestar.channels import ChannelsPlugin
from litestar.response import ServerSentEvent

from app.domain.chat.dtos import WriteDTO, ReadDTO
from app.domain.chat.schemas import Chat
from app.domain.chat.deps import provide_chat_service

from app.domain.chat.service import ChatService
from uuid import UUID
from app.db import models as m


class StreamController(Controller):
    path = "/api/stream"
    tags = ["Chats"]
    return_dto = ReadDTO
    dto = WriteDTO
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
    async def notify(self, topic: str, data: m.Chat, channels: ChannelsPlugin, chat_service: ChatService) -> None:
        chat_obj = await chat_service.create(data=data)
        message = chat_service.to_schema(data=chat_obj, schema_type=Chat)
        channels.publish(message, [topic])

    @post("/chats/create")
    async def create_message(self, data: m.Chat, chat_service: ChatService) -> m.Chat:
        return await chat_service.create(data=data)

    @get("/chats/list/{sprint_id:uuid}")
    async def get_messages(self, sprint_id: UUID, chat_service: ChatService) -> Sequence[m.Chat]:

        return await chat_service.list(sprint_id=sprint_id)
