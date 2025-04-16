from litestar.dto import DTOConfig
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO

from app.db.models import Chat
from typing import Annotated


__all__ = ["ReadDTO", "WriteDTO"]

WriteDTO = SQLAlchemyDTO[
    Annotated[Chat, DTOConfig(exclude={"id", "created_at", "updated_at", "replies", "parent"}, max_nested_depth=2)]
]
ReadDTO = SQLAlchemyDTO[Annotated[Chat, DTOConfig(exclude={"audits"}, max_nested_depth=2)]]
