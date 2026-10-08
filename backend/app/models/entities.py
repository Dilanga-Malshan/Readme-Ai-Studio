import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, JSON, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

def now():
    return datetime.now(timezone.utc)
def uid():
    return str(uuid.uuid4())

class Record:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class User(Record, Base):
    __tablename__ = 'users'
    github_id: Mapped[str] = mapped_column(String(30), unique=True)
    login: Mapped[str] = mapped_column(String(39))

class GitHubAccount(Record, Base):
    __tablename__ = 'github_accounts'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), unique=True)
    token_ciphertext: Mapped[str] = mapped_column(Text)

class AuthSession(Record, Base):
    __tablename__ = 'auth_sessions'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf_token: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class OAuthState(Record, Base):
    __tablename__ = 'oauth_states'
    state_hash: Mapped[str] = mapped_column(String(64), unique=True)
    verifier: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class ProfileSnapshot(Record, Base):
    __tablename__ = 'github_profile_snapshots'
    username: Mapped[str] = mapped_column(String(39), index=True)
    data: Mapped[dict] = mapped_column(JSON)

class ReadmeProject(Record, Base):
    __tablename__ = 'readme_projects'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(120))
    markdown: Mapped[str] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    revision: Mapped[int] = mapped_column(Integer, default=1)

class ReadmeVersion(Record, Base):
    __tablename__ = 'readme_versions'
    __table_args__ = (UniqueConstraint('project_id', 'revision'),)
    project_id: Mapped[str] = mapped_column(ForeignKey('readme_projects.id'), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    markdown: Mapped[str] = mapped_column(Text)

class Template(Record, Base):
    __tablename__ = 'templates'
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    data: Mapped[dict] = mapped_column(JSON)

class UserPreference(Record, Base):
    __tablename__ = 'user_preferences'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), unique=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)

class GenerationHistory(Record, Base):
    __tablename__ = 'generation_history'
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    client_key: Mapped[str] = mapped_column(String(64), index=True)
    operation: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(80))

class PublishHistory(Record, Base):
    __tablename__ = 'publish_history'
    __table_args__ = (UniqueConstraint('user_id', 'idempotency_key'),)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(80))
    request_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    result: Mapped[dict] = mapped_column(JSON, default=dict)


class ReadmeShare(Record, Base):
    __tablename__ = 'readme_shares'
    project_id: Mapped[str] = mapped_column(ForeignKey('readme_projects.id'), unique=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    markdown: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class GenerationBudget(Record, Base):
    __tablename__ = 'generation_budgets'
    __table_args__ = (UniqueConstraint('client_key', 'day'),)
    client_key: Mapped[str] = mapped_column(String(64), index=True)
    day: Mapped[str] = mapped_column(String(10))
    used: Mapped[int] = mapped_column(Integer, default=0)
