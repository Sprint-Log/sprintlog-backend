# pyright: reportGeneralTypeIssues=false

from typing import Any

from litestar import (
    Controller,
    get,  # pylint: disable=unused-import
    post,
)
from litestar.exceptions import NotFoundException
from litestar.params import Dependency
from livekit import AccessToken, RoomServiceClient, VideoGrant, models  # type: ignore

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.schemas import User
from app.lib.settings import server

__all__ = ["ApiController"]


validation_skip: Any = Dependency(skip_validation=True)


class ApiController(Controller):
    path = "/api/live/rooms"
    tags = ["Livekit Room API"]
    room_route = "/{room_id:str}"
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

    @get(sync_to_thread=True)
    async def list_all(self) -> list[models.Room]:
        """Get a list of Models."""
        rooms: list[models.Room] = RoomServiceClient(
            server.LIVE_API_URL, server.LIVE_API_KEY, server.LIVE_API_SECRET
        ).list_rooms()
        return rooms

    @post(room_route, sync_to_thread=True)
    async def create(self, room_id: str, current_user: User) -> str:
        grant = VideoGrant(room_join=True, room=room_id)
        access_token = AccessToken(
            server.LIVE_API_KEY,
            server.LIVE_API_SECRET,
            grant=grant,
            identity=current_user.id,
            name=current_user.email,
        )
        token: str = access_token.to_jwt()

        return token
