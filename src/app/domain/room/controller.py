# pyright: reportGeneralTypeIssues=false

from dataclasses import dataclass
from typing import Any

from litestar import (
    Controller,
    get,  # pylint: disable=unused-import
)
from litestar.exceptions import NotFoundException
from litestar.params import Dependency
from livekit import AccessToken, RoomServiceClient, VideoGrant, models  # type: ignore

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.schemas import User
from app.lib.settings import server

__all__ = ["ApiController"]


validation_skip: Any = Dependency(skip_validation=True)


@dataclass
class Token:
    room: str
    token: str


class ApiController(Controller):
    path = "/api/live/rooms"
    tags = ["Livekit Room API"]
    room_open_route = "open/{room_id:str}/{user_id:str}"
    room_list_route = "list/{room_id:str}"
    guards = [requires_active_user]

    @get(room_list_route, sync_to_thread=True)
    async def retrieve(self, room_id: str) -> models.Room:
        """Get a list of Models."""
        rooms: list[models.Room] = RoomServiceClient(
            server.LIVE_API_URL, server.LIVE_API_KEY, server.LIVE_API_SECRET
        ).list_rooms()
        for room in rooms:
            if room.sid == room_id:
                return room
        raise NotFoundException()

    @get(sync_to_thread=True)
    async def list_all(self) -> list[models.Room]:
        """Get a list of Models."""
        rooms: list[models.Room] = RoomServiceClient(
            server.LIVE_API_URL, server.LIVE_API_KEY, server.LIVE_API_SECRET
        ).list_rooms()
        return rooms

    @get(room_open_route, sync_to_thread=True)
    async def token(self, room_id: str, user_id: str, current_user: User) -> Token:
        grant = VideoGrant(
            room_join=True,
            room=room_id,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
            room_create=True,
            room_list=True,
            room_admin=True,
        )

        access_token = AccessToken(
            server.LIVE_API_KEY,
            server.LIVE_API_SECRET,
            grant=grant,
            identity=user_id,
            name=user_id,
        )

        return Token(room=room_id, token=access_token.to_jwt())
