"""Application configuration via environment variables."""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "ML-Enabled ERP Inventory Intelligence API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database (PostgreSQL or SQLite for local testing)
    database_url: str = "sqlite:///./erp_inventory.db"
    database_echo: bool = False

    # JWT
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS (for frontend)
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3002"]

    # ML export
    ml_export_max_rows: int = 1_000_000

    # ML inference (optional: path to trained model dir from ml_pipeline)
    ml_model_dir: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
