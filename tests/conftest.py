import pathlib

import pytest

from linguee_api.downloaders.error_downloader import ErrorDownloader
from linguee_api.downloaders.file_cache import FileCache


@pytest.fixture
def examples_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parents[1] / "examples"


@pytest.fixture
def examples_downloader(examples_dir) -> FileCache:
    return FileCache(cache_directory=examples_dir, upstream=ErrorDownloader())
