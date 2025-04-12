from collections.abc import AsyncGenerator
from typing import Any

from litestar import Controller, get, post
from litestar.channels import ChannelsPlugin
from litestar.response import ServerSentEvent


class Stream(Controller):
    path = "/stream"
    @get("/events/{topic:str}")
    async def get_notified(self,
            topic: str,
            channels: ChannelsPlugin
    ) -> ServerSentEvent:
        async def generator() -> AsyncGenerator[bytes, Any]:
            async with channels.start_subscription([topic]) as subscriber:
                await channels.put_subscriber_history(subscriber, [topic], limit=100)
                async for event in subscriber.iter_events():
                    yield event

        return ServerSentEvent(generator(), event_type="stream")

    @post("/notify/{topic:str}")
    async def notify(self,topic: str, data: dict, channels: ChannelsPlugin) -> None:
        channels.publish(str(data), [topic])

