from typing import Literal
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",  # Ignore extra fields in .env
    )

    # Application settings
    app_name: str = "Photobooth Kiosk API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=True)
    environment: Literal["development", "staging", "production"] = "development"

    # Database settings
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/photobooth",
    )
    database_pool_size: int = Field(default=20, ge=1, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=50)

    # Security settings
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production-min-32-chars",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = Field(default=8, ge=1, le=168)  # Max 1 week
    admin_token_expire_hours: int = Field(default=24, ge=1, le=168)

    # WebSocket settings
    ws_heartbeat_interval: int = Field(default=30, ge=10, le=300)  # seconds

    # iPaymu settings
    ipaymu_va: str = Field(default="0000005155258811")
    ipaymu_key: str = Field(
        default="SANDBOX4DDE84C3-7D3A-4572-8178-33DF5B494131",
    )
    ipaymu_url: str = Field(
        default="https://sandbox.ipaymu.com",
    )
    ipaymu_notify_url: str = Field(
        default="http://localhost:8000/api/payment/notify",
    )

    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def async_database_url(self) -> str:
        """Ensure async driver is used."""
        url = str(self.database_url)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


# Global settings instance
settings = Settings()
