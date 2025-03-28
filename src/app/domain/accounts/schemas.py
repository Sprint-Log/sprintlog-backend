from __future__ import annotations

from datetime import datetime  # noqa: TC003
from uuid import UUID


from app.db.models.team_member import TeamRoles
from app.lib.schema import CamelizedBaseStruct

__all__ = (
    "AccountLogin",
    "AccountRegister",
    "User",
    "UserCreate",
    "UserRole",
    "UserRoleAdd",
    "UserRoleRevoke",
    "UserTeam",
    "UserUpdate",
)


class UserTeam(CamelizedBaseStruct):
    """Holds team details for a user.

    This is nested in the User Model for 'team'
    """

    team_id: UUID
    team_name: str
    is_owner: bool = False
    role: TeamRoles = TeamRoles.MEMBER


class UserRole(CamelizedBaseStruct):
    """Holds role details for a user.

    This is nested in the User Model for 'roles'
    """

    role_id: UUID
    role_slug: str
    role_name: str
    assigned_at: datetime


class OauthAccount(CamelizedBaseStruct):
    """Holds linked Oauth details for a user."""

    id: UUID
    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    expires_at: int | None = None
    refresh_token: str | None = None


class User(CamelizedBaseStruct):
    """User properties to use for a response."""

    id: UUID
    email: str
    name: str | None = None
    position: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    is_superuser: bool = False
    is_active: bool = True
    is_verified: bool = False
    has_password: bool = False
    teams: list[UserTeam] = []
    bank_accounts: list[BankAccount] = []


class UserCreate(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None
    position: str | None = None
    address: str | None = None
    is_superuser: bool = False
    avatar_url: str | None = None
    bank_accounts: list[BankAccount] | None = None


class BankAccount(CamelizedBaseStruct):
    """Bank account details for a user."""

    method: str
    account_number: str


class BankAccountDetail(CamelizedBaseStruct):
    """Bank account details for a user."""

    id: UUID
    method: str
    account_number: str


class UserUpdate(CamelizedBaseStruct, omit_defaults=True):
    password: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    is_superuser: bool | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserUpdatePassword(CamelizedBaseStruct):
    old_password: str
    new_password: str
    confirm_password: str


class AccountLogin(CamelizedBaseStruct):
    username: str
    password: str


class AccountRegister(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None


class UserRoleAdd(CamelizedBaseStruct):
    """User role add ."""

    user_name: str


class UserRoleRevoke(CamelizedBaseStruct):
    """User role revoke ."""

    user_name: str
