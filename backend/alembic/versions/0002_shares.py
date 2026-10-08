"""Revocable, opt-in share snapshots."""
from alembic import op
import sqlalchemy as sa
revision='0002'
down_revision='0001'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('readme_shares',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('project_id',sa.String(36),sa.ForeignKey('readme_projects.id'),nullable=False,unique=True),
        sa.Column('token_hash',sa.String(64),nullable=False,unique=True),
        sa.Column('markdown',sa.Text(),nullable=False),
        sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False))
def downgrade(): op.drop_table('readme_shares')
