from uuid import UUID

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler

from app.db.models.team_member import TeamRoles

__all__ = ["requires_team_membership", "requires_team_ownership"]


def requires_team_membership(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Verify the connection user is a member of the team.

    Args:
        connection (ASGIConnection): _description_
        _ (BaseRouteHandler): _description_

    Raises:
        PermissionDeniedException: _description_
    """
    if connection.user.is_superuser:
        return
    team_id = connection.path_params["team_id"]
    has_team_role = any(membership.team.id == team_id for membership in connection.user.teams)
    if connection.user.is_superuser or has_team_role:
        return
    raise PermissionDeniedException(detail="Insufficient permissions to access team.")


def requires_team_ownership(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Verify that the connection user is the team owner or the team Admin. if the user is a superuser, allow access.

    Args:
        connection (ASGIConnection): _description_
        _ (BaseRouteHandler): _description_

    Raises:
        PermissionDeniedException: _description_
    """
    if connection.user.is_superuser:
        return
    team_id = UUID(connection.path_params["team_id"])
    has_team_role = any(
        membership.team.id == team_id and (membership.role == TeamRoles.ADMIN or membership.is_owner)
        for membership in connection.user.teams
    )
    if connection.user.is_superuser or has_team_role:
        return

    msg = "Insufficient permissions to access team."
    raise PermissionDeniedException(detail=msg)
