"""typeenum_str

Revision ID: 2dc4cdce2323
Revises: aa342787069a
Create Date: 2023-06-01 13:14:10.781198

"""
import sqlalchemy as sa
from alembic import op
from litestar.contrib.sqlalchemy.types import GUID
from sqlalchemy.dialects import postgresql

__all__ = ["downgrade", "upgrade"]


sa.GUID = GUID

# revision identifiers, used by Alembic.
revision = "2dc4cdce2323"
down_revision = "aa342787069a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "backlog",
        "type",
        existing_type=postgresql.ENUM("backlog", "task", "draft", name="itemtype"),
        type_=sa.String(length=50),
        existing_nullable=False,
        existing_server_default=sa.text("'backlog'::itemtype"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "backlog",
        "type",
        existing_type=sa.String(length=50),
        type_=postgresql.ENUM("backlog", "task", "draft", name="itemtype"),
        existing_nullable=False,
        existing_server_default=sa.text("'backlog'::itemtype"),
    )
    # ### end Alembic commands ###
