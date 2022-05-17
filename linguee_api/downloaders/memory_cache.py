from typing import Dict

from linguee_api.downloaders.interfaces import IDownloader


class MemoryCache(IDownloader):
    """
    Memory cache.

    Exposes the downloader interface, but requires the upstream to work and
    keeps records in memory.
    """

    def __init__(self, upstream: IDownloader):
        self.upstream = upstream
        self.cache: Dict[str, str] = {}

    async def download(self, url: str) -> str:
        if url not in self.cache:
            self.cache[url] = await self.upstream.download(url)
        return self.cache[url]
