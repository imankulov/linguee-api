import pytest
from pydantic import BaseSettings, Field

from linguee_api.config import settings
from linguee_api.const import PROJECT_ROOT
from linguee_api.downloaders.error_downloader import ErrorDownloader
from linguee_api.downloaders.file_cache import FileCache
from linguee_api.downloaders.httpx_downloader import HTTPXDownloader
from linguee_api.downloaders.interfaces import IDownloader
from linguee_api.linguee_client import LingueeClient
from linguee_api.parsers import XExtractParser


class PytestSettings(BaseSettings):
    """Specific settings for pytest."""

    offline: bool = Field(default=False, description="Run tests offline")

    @property
    def downloader(self) -> IDownloader:
        return ErrorDownloader() if self.offline else HTTPXDownloader()

    class Config:
        env_prefix = "pytest_"
        env_file = (PROJECT_ROOT / ".env").as_posix()


pytest_settings = PytestSettings()


@pytest.fixture
def examples_downloader() -> FileCache:
    return FileCache(
        cache_directory=settings.cache_directory, upstream=pytest_settings.downloader
    )


@pytest.fixture
def linguee_client(examples_downloader) -> LingueeClient:
    return LingueeClient(
        page_downloader=examples_downloader, page_parser=XExtractParser()
    )
