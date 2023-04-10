from typing import TYPE_CHECKING, Any

from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedColumn as MCol
from sqlalchemy.orm import registry

from app.domain.users import User
from app.lib import dto, orm, service
from app.lib.repository.sqlalchemy import SQLAlchemyRepository
from app.lib.worker import queue

if TYPE_CHECKING:
    from uuid import UUID

from sqlalchemy.orm import relationship


class Task(orm.Base):
    registry = registry(
        type_annotation_map={User: User},
    )
    title: Mapped[str] = MCol(String)
    description: Mapped[str] = MCol(String)
    progress: Mapped[int] = MCol(Integer, default=0)
    sprint_number: Mapped[int] = MCol(Integer)
    project_slug: Mapped[str] = MCol(String)
    priority: Mapped[int] = MCol(Integer)
    status: Mapped[str] = MCol(String)
    is_backlog: Mapped[bool] = MCol(Boolean)
    labels: Mapped[list | None] = MCol(ARRAY(String), nullable=True)
    tags: Mapped[list | None] = MCol(ARRAY(String), nullable=True)
    assigner: Mapped["User" | None] = relationship(
        back_populates="tasks_managed", foreign_keys=["assigner_id"]
    )
    assignee: Mapped["User" | None] = relationship(
        back_populates="tasks_owned", foreign_keys=["assignee_id"]
    )
    assigner_id: Mapped["UUID" | None] = MCol(ForeignKey("user.id"))
    assignee_id: Mapped["UUID" | None] = MCol(ForeignKey("user.id"))


class Repository(SQLAlchemyRepository[Task]):
    model_type = Task


class Service(service.Service[Task]):
    async def create(self, data: Task) -> Task:
        created = await super().create(data)
        await queue.enqueue("task_created", data=ReadDTO.from_orm(created).dict())
        return created

    async def update(self, id_: "UUID", data: Task) -> Task:
        updated = await super().update(id_, data)
        await queue.enqueue("task_updated", data=ReadDTO.from_orm(updated).dict())
        return updated

    async def delete(self, id_: "UUID") -> Any:
        deleted = await super().delete(id_)
        await queue.enqueue("task_delete", data=ReadDTO.from_orm(deleted).dict())
        return deleted

    @staticmethod
    async def create_zulip_topic(message_content: str) -> None:
        """Sends an email to alert that a new `Task` has been created.

        Args:
            message_content: The body of the email.
        """
        # print(message_content)

    @staticmethod
    async def update_zulip_topic(message_content: str) -> None:
        """Sends an email to alert that a new `Task` has been created.

        Args:
            message_content: The body of the email.
        """
        # print(message_content)

    @staticmethod
    async def delete_zulip_topic(message_content: str) -> None:
        """Sends an email to alert that a new `Task` has been created.

        Args:
            message_content: The body of the email.
        """
        # print(message_content)


CreateDTO = dto.factory(
    "TaskCreateDTO", Task, purpose=dto.Purpose.write, exclude={"id"}
)
ReadDTO = dto.factory("TaskReadDTO", Task, purpose=dto.Purpose.read)
WriteDTO = dto.factory("TaskWriteDTO", Task, purpose=dto.Purpose.write)
