import pathlib

import pytest

from linguee_api.downloaders.error_downloader import ErrorDownloader
from linguee_api.downloaders.file_cache import FileCache
from linguee_api.linguee_client import LingueeClient
from linguee_api.parsers import XExtractParser


@pytest.fixture
def examples_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parents[1] / "examples"


@pytest.fixture
def examples_downloader(examples_dir) -> FileCache:
    return FileCache(cache_directory=examples_dir, upstream=ErrorDownloader())


@pytest.fixture
def linguee_client(examples_downloader) -> LingueeClient:
    return LingueeClient(
        page_downloader=examples_downloader, page_parser=XExtractParser()
    )
