# type: ignore
"""resolve conflict issue for local and dev db

Revision ID: a62993d5e879
Revises: 86e3d9a80486
Create Date: 2025-03-27 09:27:28.225454+00:00

"""
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import DATE
import sqlalchemy as sa
from alembic import op
from advanced_alchemy.types import EncryptedString, EncryptedText, GUID, ORA_JSONB, DateTimeUTC

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["downgrade", "upgrade", "schema_upgrades", "schema_downgrades", "data_upgrades", "data_downgrades"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB
sa.EncryptedString = EncryptedString
sa.EncryptedText = EncryptedText

# revision identifiers, used by Alembic.
revision = "a62993d5e879"
down_revision = "86e3d9a80486"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            schema_upgrades()
            data_upgrades()


def downgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            data_downgrades()
            schema_downgrades()


def schema_upgrades() -> None:
    """schema upgrade migrations go here."""
    conn = op.get_bind()
    insp = sa.inspect(conn)

    audit_columns = [col["name"] for col in insp.get_columns("audit")]
    with op.batch_alter_table("audit", schema=None) as batch_op:

        if "sa_orm_sentinel" not in audit_columns:
            batch_op.add_column(sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True))

        if "_sentinel" in audit_columns:
            batch_op.drop_column("_sentinel")

    existing_indexes = [idx["name"] for idx in insp.get_indexes("project")]
    with op.batch_alter_table("project", schema=None) as batch_op:
        if "ix_project_slug_unique" not in existing_indexes:
            batch_op.create_index("ix_project_slug_unique", ["slug"], unique=True)

    tag_columns = [col["name"] for col in insp.get_columns("tag")]
    tag_indexes = [idx["name"] for idx in insp.get_indexes("tag")]
    with op.batch_alter_table("tag", schema=None) as batch_op:
        if "slug" not in tag_columns:
            batch_op.add_column(sa.Column("slug", sa.String(length=100), nullable=False))
        if "ix_tag_slug_unique" not in tag_indexes:
            batch_op.create_index("ix_tag_slug_unique", ["slug"], unique=True)

        batch_op.drop_table_comment(existing_comment="Tags that can be applied to various objects")

    team_indexes = [idx["name"] for idx in insp.get_indexes("team")]
    with op.batch_alter_table("team", schema=None) as batch_op:
        if "ix_team_slug" in team_indexes:
            batch_op.drop_index("ix_team_slug")
        if "ix_team_slug_unique" not in team_indexes:
            batch_op.create_index("ix_team_slug_unique", ["slug"], unique=True)

    user_columns = [col["name"] for col in insp.get_columns("user_account")]
    with op.batch_alter_table("user_account", schema=None) as batch_op:

        if "avatar_url" not in user_columns:
            batch_op.add_column(sa.Column("avatar_url", sa.String(length=500), nullable=True))

        if "joined_at" not in user_columns:
            batch_op.add_column(
                sa.Column("joined_at", sa.Date(), nullable=False, server_default=sa.func.current_date())
            )

            batch_op.alter_column(
                "joined_at",
                server_default=None,
                existing_type=DATE(),
                existing_nullable=False,
            )


def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # --- USER_ACCOUNT ---
    user_columns = [col["name"] for col in insp.get_columns("user_account")]
    with op.batch_alter_table("user_account", schema=None) as batch_op:
        if "joined_at" in user_columns:
            batch_op.drop_column("joined_at")
        if "avatar_url" in user_columns:
            batch_op.drop_column("avatar_url")

    # --- TEAM ---
    team_uniques = [uc["name"] for uc in insp.get_unique_constraints("team")]
    team_indexes = [idx["name"] for idx in insp.get_indexes("team")]
    with op.batch_alter_table("team", schema=None) as batch_op:
        if "uq_team_slug" in team_uniques:
            batch_op.drop_constraint("uq_team_slug", type_="unique")

        if "ix_team_slug_unique" in team_indexes:
            batch_op.drop_index("ix_team_slug_unique")

        # Only create 'ix_team_slug' if it's not already there.
        if "ix_team_slug" not in team_indexes:
            batch_op.create_index("ix_team_slug", ["slug"], unique=True)

    # --- TAG ---
    tag_uniques = [uc["name"] for uc in insp.get_unique_constraints("tag")]
    tag_indexes = [idx["name"] for idx in insp.get_indexes("tag")]
    tag_columns = [col["name"] for col in insp.get_columns("tag")]
    with op.batch_alter_table("tag", schema=None) as batch_op:
        # Table comments can’t really be “checked,” so we’ll just set them unconditionally:
        batch_op.create_table_comment("Tags that can be applied to various objects", existing_comment=None)

        if "uq_tag_slug" in tag_uniques:
            batch_op.drop_constraint("uq_tag_slug", type_="unique")

        if "ix_tag_slug_unique" in tag_indexes:
            batch_op.drop_index("ix_tag_slug_unique")

        if "slug" in tag_columns:
            batch_op.drop_column("slug")

    # --- PROJECT ---
    project_indexes = [idx["name"] for idx in insp.get_indexes("project")]
    with op.batch_alter_table("project", schema=None) as batch_op:
        if "ix_project_slug_unique" in project_indexes:
            batch_op.drop_index("ix_project_slug_unique")

    # --- AUDIT ---
    audit_columns = [col["name"] for col in insp.get_columns("audit")]
    with op.batch_alter_table("audit", schema=None) as batch_op:
        # Drop 'sa_orm_sentinel' if it exists
        if "sa_orm_sentinel" in audit_columns:
            batch_op.drop_column("sa_orm_sentinel")

        # Only add '_sentinel' if it doesn't exist
        if "_sentinel" not in audit_columns:
            batch_op.add_column(sa.Column("_sentinel", sa.Integer(), autoincrement=False, nullable=True))


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
