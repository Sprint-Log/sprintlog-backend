from litestar.dto import DTOConfig
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO

from app.db.models import SprintLog
from typing import Annotated


__all__ = ["ReadDTO", "WriteDTO"]

WriteDTO = SQLAlchemyDTO[
    Annotated[SprintLog, DTOConfig(exclude={"id", "created_at", "updated_at", "chats"}, max_nested_depth=2)]
]
ReadDTO = SQLAlchemyDTO[Annotated[SprintLog, DTOConfig(exclude={"audits"}, max_nested_depth=2)]]
