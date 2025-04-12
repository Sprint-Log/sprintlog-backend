from contextlib import asynccontextmanager
from typing import AsyncContextManager

from litestar import WebSocket, websocket_listener
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect


@asynccontextmanager
async def chat_room_lifespan(
    socket: WebSocket, channels: ChannelsPlugin
) -> AsyncContextManager[None]:
    async with channels.start_subscription(
        socket.path_params["chan"], history=10
    ) as subscriber:
        try:
            async with subscriber.run_in_background(socket.send_data):
                yield
        except WebSocketDisconnect:
            return


@websocket_listener("/ws/{chan:str}", connection_lifespan=chat_room_lifespan)
async def chat_handler(data: str, chan: str, channels: ChannelsPlugin) -> None:
    channels.publish(data, chan)

