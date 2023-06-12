"""plugin_meta

Revision ID: 1296e146605c
Revises: 48c4e39b77bb
Create Date: 2023-06-13 04:02:22.638163

"""
import sqlalchemy as sa
from alembic import op
from litestar.contrib.sqlalchemy.types import GUID

__all__ = ["downgrade", "upgrade"]


sa.GUID = GUID

# revision identifiers, used by Alembic.
revision = "1296e146605c"
down_revision = "48c4e39b77bb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("backlog", sa.Column("plugin_meta", sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("backlog", "plugin_meta")
    # ### end Alembic commands ###
