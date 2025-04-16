from __future__ import annotations
from app.lib.schema import CamelizedBaseStruct
from app.db.models.enums import ChatType, EventType
from typing import Optional
from uuid import UUID


class ChatCreate(CamelizedBaseStruct):
    message: str
    chat_type: ChatType
    event_type: EventType
    sprint_id: UUID
    parent_id: Optional[UUID] = None


class Chat(CamelizedBaseStruct):
    id: UUID
    message: str
    chat_type: ChatType
    event_type: EventType
    sprint_id: UUID
    parent_id: Optional[UUID] = None
    replies: list["Chat"] = []
    parent: Optional["Chat"] = None
