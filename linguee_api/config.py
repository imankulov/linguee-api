import pathlib
from typing import Optional

from pydantic import BaseSettings

from linguee_api.const import PROJECT_ROOT


class Settings(BaseSettings):
    """Application settings."""

    # Sentry settings
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"

    # File cache settings
    cache_directory: pathlib.Path = PROJECT_ROOT / ".cache"

    class Config:
        env_file = (PROJECT_ROOT / ".env").as_posix()


settings = Settings()
