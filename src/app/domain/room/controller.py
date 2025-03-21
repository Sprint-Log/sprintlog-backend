from __future__ import annotations

from typing import Any, List

from dataclasses import dataclass
from datetime import timedelta
from litestar import Controller, get
from litestar.exceptions import NotFoundException
from litestar.params import Dependency

from livekit import api

from app.domain.accounts.guards import requires_active_user
from app.domain.accounts.schemas import User
from app.config.base import get_settings

from livekit.protocol.models import Room

settings = get_settings()
server = settings.server

__all__ = ["RoomController"]

validation_skip: Any = Dependency(skip_validation=True)


@dataclass
class Token:
    room: str
    token: str


class RoomController(Controller):

    path = "/api/live/rooms"
    tags = ["Livekit Room API"]
    guards = [requires_active_user]

    # Example routes
    room_open_route = "open/{room_id:str}/{user_id:str}"
    room_detail = "list/{room_id:str}"
    room_list = "list"

    @get(room_detail)
    async def get_room(self, room_id: str) -> Room:
        """Return details for a specific room or raise 404 if not found."""
        lkapi = api.LiveKitAPI(
            url=server.LIVE_API_URL,
            api_key=server.LIVE_API_KEY,
            api_secret=server.LIVE_API_SECRET,
        )
        try:
            response = await lkapi.room.list_rooms(api.ListRoomsRequest())
            if not response.rooms:
                raise NotFoundException("No rooms found")

            for room in response.rooms:
                if room.sid == room_id:
                    return room
            raise NotFoundException(f"Room with SID '{room_id}' not found")
        finally:
            await lkapi.aclose()

    @get(room_list)
    async def list_all_rooms(self) -> List[Room]:
        """Get all active rooms."""
        lkapi = api.LiveKitAPI(
            url=server.LIVE_API_URL,
            api_key=server.LIVE_API_KEY,
            api_secret=server.LIVE_API_SECRET,
        )
        roomResponse = await lkapi.room.list_rooms(api.ListRoomsRequest())

        return list(roomResponse.rooms)

    @get(room_open_route)
    async def token(self, room_id: str, user_id: str, current_user: User) -> Token:
        """
        Generate a LiveKit token to join (or interact with) the specified room.
        """

        access_token = (
            api.AccessToken(api_key=server.LIVE_API_KEY, api_secret=server.LIVE_API_SECRET)
            .with_identity(user_id)
            .with_ttl(ttl=timedelta(days=1))
            .with_name(name=user_id)
        )
        grant = api.VideoGrants(
            room_join=True,
            room=room_id,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
            room_create=True,
            room_list=True,
            room_admin=True,
        )

        access_token.with_grants(grant)

        token_str = access_token.to_jwt()

        return Token(room=room_id, token=token_str)
