from typing import TYPE_CHECKING

from .tasks import task_created, task_deleted, task_updated

if TYPE_CHECKING:
    from app.lib.worker import WorkerFunction

functions: list["WorkerFunction"] = [task_created, task_deleted, task_updated]
