from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vacation Rental API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://rental:rental@localhost:5432/rental"
    cors_origins: str = "http://localhost:4200"
    frontend_url: str = "http://localhost:4200"
    backend_url: str = "http://localhost:8000"
    jwt_secret_key: str = "change-me-in-development"
    jwt_algorithm: str = "HS256"
    admin_access_token_expire_minutes: int = 15
    admin_refresh_token_expire_days: int = 14
    admin_cookie_secure: bool | None = None
    admin_cookie_samesite: str = "lax"
    booking_hold_minutes: int = 15
    max_ical_bytes: int = 1_000_000
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def secure_cookies(self) -> bool:
        return self.is_production if self.admin_cookie_secure is None else self.admin_cookie_secure


@lru_cache
def get_settings() -> Settings:
    return Settings()
