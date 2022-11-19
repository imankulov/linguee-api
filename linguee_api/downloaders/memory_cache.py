from async_lru import alru_cache

from linguee_api.downloaders.interfaces import IDownloader


class MemoryCache(IDownloader):
    """Memory cache.

    Exposes the downloader interface, but requires the upstream to work and
    keeps records in memory.
    """

    def __init__(self, upstream: IDownloader, maxsize: int = 1000):
        self.upstream = upstream
        self.download = alru_cache(maxsize=maxsize)(self.download)  # type: ignore

    async def download(self, url: str) -> str:
        return await self.upstream.download(url)
