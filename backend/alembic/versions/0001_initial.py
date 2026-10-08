"""Initial normalized schema. Frozen metadata for reproducible migrations."""
from alembic import op
import sqlalchemy as sa
revision='0001'
down_revision=None
branch_labels=None
depends_on=None
TABLES={
'users':[sa.Column('github_id',sa.String(30),nullable=False,unique=True),sa.Column('login',sa.String(39),nullable=False)],
'github_accounts':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False,unique=True),sa.Column('token_ciphertext',sa.Text(),nullable=False)],
'auth_sessions':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False,index=True),sa.Column('token_hash',sa.String(64),nullable=False,unique=True),sa.Column('csrf_token',sa.String(64),nullable=False),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False)],
'oauth_states':[sa.Column('state_hash',sa.String(64),nullable=False,unique=True),sa.Column('verifier',sa.String(128),nullable=False),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False)],
'github_profile_snapshots':[sa.Column('username',sa.String(39),nullable=False,index=True),sa.Column('data',sa.JSON(),nullable=False)],
'readme_projects':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False,index=True),sa.Column('title',sa.String(120),nullable=False),sa.Column('markdown',sa.Text(),nullable=False),sa.Column('config',sa.JSON(),nullable=False),sa.Column('revision',sa.Integer(),nullable=False)],
'readme_versions':[sa.Column('project_id',sa.String(36),sa.ForeignKey('readme_projects.id'),nullable=False,index=True),sa.Column('revision',sa.Integer(),nullable=False),sa.Column('markdown',sa.Text(),nullable=False),sa.UniqueConstraint('project_id','revision')],
'templates':[sa.Column('slug',sa.String(50),nullable=False,unique=True),sa.Column('data',sa.JSON(),nullable=False)],
'user_preferences':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False,unique=True),sa.Column('data',sa.JSON(),nullable=False)],
'generation_history':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=True,index=True),sa.Column('client_key',sa.String(64),nullable=False,index=True),sa.Column('operation',sa.String(30),nullable=False),sa.Column('model',sa.String(80),nullable=False)],
'publish_history':[sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False,index=True),sa.Column('idempotency_key',sa.String(80),nullable=False),sa.Column('request_hash',sa.String(64),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('result',sa.JSON(),nullable=False),sa.UniqueConstraint('user_id','idempotency_key')]
}
def upgrade():
    for name,columns in TABLES.items():
        op.create_table(name,sa.Column('id',sa.String(36),primary_key=True),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),*columns)
def downgrade():
    for name in reversed(TABLES): op.drop_table(name)
