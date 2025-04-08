from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler
from app.config.app import alchemy
from app.domain.sprintlogs.dependencies import provide_sprintlog_service

__all__ = ["requires_project_assignee", "requires_project_owner"]


async def requires_project_assignee(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """
    Guard that ensures the current user is a member of a team assigned to the project.
    Allows superusers to bypass the check.
    """
    if connection.user.is_superuser:
        return

    # Collect user team IDs
    user_team_ids = {membership.team.id for membership in connection.user.teams}

    sprintlog_slug = connection.path_params.get("slug")
    sprintlog_id = connection.path_params.get("row_id")

    if not sprintlog_slug and not sprintlog_id:
        raise PermissionDeniedException("Sprintlog identifier is missing from the path.")

    session = alchemy.provide_session(connection.app.state, connection.scope)
    sprintlog_service = await anext(provide_sprintlog_service(session))

    if sprintlog_slug:
        sprintlog = await sprintlog_service.repository.get_by_slug(sprintlog_slug)
    else:
        sprintlog = await sprintlog_service.get_one_or_none(id=sprintlog_id)

    if not sprintlog:
        raise PermissionDeniedException(detail="Sprintlog not found.")

    assigned_team_ids = {team.id for team in sprintlog.project.teams}
    if user_team_ids & assigned_team_ids:
        return

    raise PermissionDeniedException(detail="You are not assigned to this project.")


async def requires_project_owner(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Verify the connection user is the onwer of the project.

    Args:
        connection (ASGIConnection): _description_
        _ (BaseRouteHandler): _description_

    Raises:
        PermissionDeniedException: _description_
    """
    if connection.user.is_superuser:
        return

    user_teams = {membership.team.id for membership in connection.user.teams}

    sprintlog_slug = connection.path_params.get("slug")
    if not sprintlog_slug:
        raise PermissionDeniedException("Sprintlog slug is missing from the path.")

    session = alchemy.provide_session(connection.app.state, connection.scope)
    sprintlog_service = await anext(provide_sprintlog_service(session))
    sprintlog = await sprintlog_service.repository.get_by_slug(sprintlog_slug)
    if not sprintlog:
        raise PermissionDeniedException(detail="Sprintlog not found.")

    if connection.user.id == sprintlog.project.owner_id:
        return

    raise PermissionDeniedException(detail="Insufficient permissions to access project.")
