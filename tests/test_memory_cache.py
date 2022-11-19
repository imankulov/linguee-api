import pytest

from linguee_api.downloaders.memory_cache import MemoryCache
from linguee_api.downloaders.mock_downloader import MockDownloader


@pytest.mark.asyncio
async def test_memory_cache_should_cache_a_value():
    # Cache value
    cache = MemoryCache(upstream=MockDownloader(message="foo"))
    await cache.download("https://example.com")

    # Change upstream and try to get the value again
    cache.upstream = MockDownloader(message="bar")
    result2 = await cache.download("https://example.com")

    # The value should be the same
    assert result2 == "foo"


@pytest.mark.asyncio
async def test_memory_cache_should_evict_cache_on_overflow():
    # Cache value
    cache = MemoryCache(upstream=MockDownloader(message="foo"), maxsize=1)
    await cache.download("https://example.com")
    await cache.download("https://example2.com")

    # Change upstream and try to get the value again
    cache.upstream = MockDownloader(message="bar")
    result2 = await cache.download("https://example.com")

    # The value should be the new one
    assert result2 == "bar"
