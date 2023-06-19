# pyright: reportGeneralTypeIssues=false

from dataclasses import dataclass
from typing import Any

import structlog
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
    room_route = "open/{room_id:str}"
    room_list_route = "list/{room_id:str}"
    guards = [requires_active_user]

    @get(room_route, sync_to_thread=True)
    async def retrieve(self, room_id: str) -> models.Room:
        """Get a list of Models."""
        rooms: list[models.Room] = RoomServiceClient(
            server.LIVE_API_URL, server.LIVE_API_KEY, server.LIVE_API_SECRET
        ).list_rooms()
        for room in rooms:
            if room.sid == room_id:
                return room
        raise NotFoundException()

    @get(room_list_route, sync_to_thread=True)
    async def list_all(self) -> list[models.Room]:
        """Get a list of Models."""
        rooms: list[models.Room] = RoomServiceClient(
            server.LIVE_API_URL, server.LIVE_API_KEY, server.LIVE_API_SECRET
        ).list_rooms()
        return rooms

    @get(sync_to_thread=True)
    async def token(self, room_id: str, current_user: User) -> Token:
        logg = structlog.get_logger()
        grant = VideoGrant(room_join=True, room=room_id)
        access_token = AccessToken(
            server.LIVE_API_KEY,
            server.LIVE_API_SECRET,
            grant=grant,
            identity=str(current_user.id),
            name=current_user.email,
        )
        logg.error("access token", access_token=access_token)

        return Token(room=room_id, token=access_token.to_jwt())
