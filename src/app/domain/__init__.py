"""Application Modules."""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.lib import settings, worker
from app.lib.worker.controllers import WorkerController

from . import accounts, analytics, backlogs, openapi, projects, security, system, teams, urls, web

if TYPE_CHECKING:
    from litestar.types import ControllerRouterHandler


routes: list[ControllerRouterHandler] = [
    projects.controllers.ApiController,
    backlogs.controllers.ApiController,
    accounts.controllers.AccessController,
    accounts.controllers.AccountController,
    teams.controllers.TeamController,
    # teams.controllers.TeamInvitationController,
    # teams.controllers.TeamMemberController,
    analytics.controllers.StatsController,
    system.controllers.SystemController,
    web.controllers.WebController,
]

if settings.worker.WEB_ENABLED:
    routes.append(WorkerController)

__all__ = [
    "tasks",
    "scheduled_tasks",
    "system",
    "accounts",
    "teams",
    "web",
    "urls",
    "security",
    "routes",
    "openapi",
    "analytics",
    "backlogs",
    "projects",
]
tasks: dict[worker.Queue, list[worker.WorkerFunction]] = {
    worker.queues.get("system-tasks"): [  # type: ignore[dict-item]
        worker.tasks.system_task,
        worker.tasks.system_upkeep,
    ],
    worker.queues.get("background-tasks"): [  # type: ignore[dict-item]
        worker.tasks.background_worker_task,
    ],
}
scheduled_tasks: dict[worker.Queue, list[worker.CronJob]] = {
    worker.queues.get("system-tasks"): [  # type: ignore[dict-item]
        worker.CronJob(function=worker.tasks.system_upkeep, unique=True, cron="0 * * * *", timeout=500),
    ],
    worker.queues.get("background-tasks"): [  # type: ignore[dict-item]
        worker.CronJob(function=worker.tasks.background_worker_task, unique=True, cron="* * * * *", timeout=300),
    ],
}
