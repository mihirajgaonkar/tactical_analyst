from functools import lru_cache
from pathlib import Path

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/tactical_analyst"
    redis_url: str = "redis://redis:6379/0"

    object_storage_provider: str = "local"
    object_storage_path: Path = Path("./data/object_store")
    s3_endpoint_url: str | None = None
    s3_bucket: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    llm_provider: str = "gemini"
    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.1
    llm_max_retries: int = 3
    llm_timeout_seconds: int = 60
    llm_retry_backoff_seconds: float = 0.5

    soccer_data_provider: str = "statsbomb_open"
    statsbomb_open_data_base_url: AnyUrl = Field(
        default="https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    )

    report_prompt_version: str = "v1"

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    cache_ttl_seconds: int = 3600
    analytics_version: str = "analytics_v1"
    max_claim_repair_attempts: int = 1


@lru_cache
def get_settings() -> Settings:
    """Return cached process-wide settings."""

    return Settings()
