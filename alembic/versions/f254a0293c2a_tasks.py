"""tasks

Revision ID: f254a0293c2a
Revises: 
Create Date: 2023-04-07 12:03:24.549618

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f254a0293c2a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('progress', sa.Integer(), nullable=False),
    sa.Column('sprint_number', sa.Integer(), nullable=False),
    sa.Column('project_slug', sa.String(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('is_closed', sa.Boolean(), nullable=False),
    sa.Column('labels', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('assigned_to', sa.String(), nullable=False),
    sa.Column('assigned_by', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_task'))
    )
    op.create_table('user',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('joined', sa.Date(), nullable=False),
    sa.Column('type', postgresql.ENUM('admin', 'regular', name='user-types-enum'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('task')
    # ### end Alembic commands ###
