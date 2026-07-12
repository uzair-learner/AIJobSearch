from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_DB = BACKEND_DIR / "visa_sponsor_jobs.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "VisaSponsor Jobs API"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api"
    frontend_url: str = "http://127.0.0.1:5173"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    admin_token: str = "change-me"
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_DB.as_posix()}"
    redis_url: str = "redis://localhost:6379/0"
    enable_demo_seed: bool = True
    max_upload_size_mb: int = 20
    request_rate_limit: int = 120
    request_rate_window_seconds: int = 60
    current_jobs_refresh_minutes: int = 180
    government_refresh_hours: int = 24
    allow_sqlite_demo: bool = True
    default_export_format: str = "csv"
    approved_download_hosts: list[str] = Field(
        default_factory=lambda: ["www.dol.gov", "download.dol.gov"]
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
