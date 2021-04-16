import abc

import httpx


class DownloaderError(Exception):
    pass


class IDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, url: str) -> str:
        """Download a page or raise an exception"""
        ...


class HTTPXDownloader(IDownloader):
    async def download(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
            except httpx.ConnectError as e:
                raise DownloaderError(str(e)) from e
            if response.status_code != 200:
                raise DownloaderError(
                    f"The Linguee server returned {response.status_code}"
                )
            return response.text
