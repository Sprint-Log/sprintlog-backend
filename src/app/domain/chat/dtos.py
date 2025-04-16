from litestar.dto import DTOConfig, DataclassDTO
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO

from app.db.models import Chat
from app.db.models.enums import ChatType, EventType

from typing import Annotated, Optional, List
from dataclasses import dataclass, field
from uuid import UUID

__all__ = ["ReadDTO", "WriteDTO"]


@dataclass
class ReadChat:
    id: UUID
    message: str
    chat_type: ChatType
    event_type: EventType
    sprint_id: UUID
    parent_id: Optional[UUID] = None
    replies: List["ReadChat"] = field(default_factory=list)
    parent: Optional["ReadChat"] = None


WriteDTO = SQLAlchemyDTO[
    Annotated[
        Chat,
        DTOConfig(
            exclude={"id", "created_at", "updated_at", "replies", "parent", "sprintlog"},
            max_nested_depth=2,
        ),
    ]
]

ReadDTO = DataclassDTO[
    Annotated[
        ReadChat,
        DTOConfig(exclude={"sprintlog"}, max_nested_depth=2),
    ]
]
