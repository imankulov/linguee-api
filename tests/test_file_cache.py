from pathlib import Path

import pytest

from linguee_api.downloaders.file_cache import FileCache
from linguee_api.downloaders.mock_downloader import MockDownloader


@pytest.mark.asyncio
async def test_file_cache_should_cache_a_value(tmp_path):
    # Cache value
    cache = FileCache(
        cache_directory=Path(tmp_path), upstream=MockDownloader(message="foo")
    )
    await cache.download("https://example.com")

    # Change upstream and try to get the value again
    cache.upstream = MockDownloader(message="bar")
    result2 = await cache.download("https://example.com")

    # The value should be the same
    assert result2 == "foo"
