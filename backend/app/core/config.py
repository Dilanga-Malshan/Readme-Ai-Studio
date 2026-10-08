from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+aiosqlite:///./readme-ai.db"
    frontend_url: str = "http://localhost:4200"
    backend_url: str = "http://localhost:8000"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_token: str = ""
    token_encryption_key: str = ""
    redis_url: str = ""
    cookie_secure: bool = False
    ai_daily_limit: int = 30
    request_limit_per_minute: int = 90
    session_hours: int = 12

@lru_cache
def settings():
    return Settings()
