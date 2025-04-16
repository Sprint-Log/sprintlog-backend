from collections.abc import AsyncGenerator
from typing import Any

from litestar import Controller, get, post
from litestar.di import Provide
from litestar.channels import ChannelsPlugin
from litestar.response import ServerSentEvent

from app.domain.chat.schemas import Chat, ChatCreate
from app.domain.chat.deps import provide_chat_service

from app.domain.chat.service import ChatService


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
    async def notify(self, topic: str, data: dict, channels: ChannelsPlugin) -> None:
        channels.publish(str(data), [topic])

    @get("/chats/{topic:str}")
    async def stream_messages(self, topic: str, channels: ChannelsPlugin) -> ServerSentEvent:
        async def generator():
            async with channels.start_subscription([topic]) as subscriber:
                async for event in subscriber.iter_events():
                    yield event

        return ServerSentEvent(generator(), event_type="message")

    # @get("/chat/{sprint_id:uuid}")
    # async def get_messages(self, sprint_id: UUID, chat_service: ChatService) -> OffsetPagination[Chat]:

    #     chats, total = await chat_service.list_and_count(sprint_id=sprint_id)
    #     return chat_service.to_schema(data=chats, total=total, schema_type=Chat)

    @post("/chats/create")
    async def create_message(self, data: ChatCreate, chat_service: ChatService) -> Chat:

        chat_obj = await chat_service.create(data=data)

        return chat_service.to_schema(data=chat_obj, schema_type=Chat)
