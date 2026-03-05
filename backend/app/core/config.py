from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Carousel Generator MVP API"
    API_PREFIX: str = "/api"
    ENV: Literal["dev", "prod", "test"] = "dev"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/carousel_mvp"
    AUTO_CREATE_DB: bool = True

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    FRONTEND_ASSET_BASE_URL: str = "http://web:3000"

    S3_ENDPOINT_URL: str = "http://minio:9000"
    S3_PUBLIC_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "us-east-1"
    S3_BUCKET_ASSETS: str = "carousel-assets"
    S3_BUCKET_EXPORTS: str = "carousel-exports"
    S3_PRESIGNED_TTL_SECONDS: int = 3600

    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_OUTPUT_TOKENS: int = 1200
    LLM_COST_PER_1K_TOKENS_USD: float = Field(default=0.002, ge=0.0)

    EXPORT_VIEWPORT_WIDTH: int = 1080
    EXPORT_VIEWPORT_HEIGHT: int = 1350

    WORKER_POLL_INTERVAL_SECONDS: float = 3.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
