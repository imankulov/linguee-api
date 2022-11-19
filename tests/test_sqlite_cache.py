from pathlib import Path

import pytest

from linguee_api.downloaders.mock_downloader import MockDownloader
from linguee_api.downloaders.sqlite_cache import SQLiteCache


@pytest.mark.asyncio
async def test_sqlite_cache_should_cache_a_value(tmp_path):
    # Cache value
    cache_database = Path(tmp_path) / "cache.db"
    cache = SQLiteCache(
        cache_database=cache_database, upstream=MockDownloader(message="foo")
    )
    await cache.download("https://example.com")

    # Change upstream and try to get the value again
    cache.upstream = MockDownloader(message="bar")
    result2 = await cache.download("https://example.com")

    # The value should be the same
    assert result2 == "foo"
