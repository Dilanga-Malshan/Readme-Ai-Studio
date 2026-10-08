"""Atomic daily AI budget counters."""
from alembic import op
import sqlalchemy as sa
revision='0003'
down_revision='0002'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('generation_budgets',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('client_key',sa.String(64),nullable=False,index=True),
        sa.Column('day',sa.String(10),nullable=False),
        sa.Column('used',sa.Integer(),nullable=False),
        sa.UniqueConstraint('client_key','day'))
def downgrade(): op.drop_table('generation_budgets')
