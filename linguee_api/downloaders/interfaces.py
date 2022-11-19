import abc
from typing import Optional


class DownloaderError(Exception):
    pass


class IDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, url: str) -> str:
        """Download a page or raise an exception"""
        ...


class ICache(IDownloader, abc.ABC):

    upstream: IDownloader

    @abc.abstractmethod
    async def get_from_cache(self, url: str) -> Optional[str]:
        """Return a page from the cache."""
        ...

    @abc.abstractmethod
    async def put_to_cache(self, url: str, page: str) -> None:
        """Put a page to the cache."""
        ...

    async def download(self, url: str) -> str:
        page = await self.get_from_cache(url)
        if page is None:
            page = await self.upstream.download(url)
            await self.put_to_cache(url, page)
        return page
