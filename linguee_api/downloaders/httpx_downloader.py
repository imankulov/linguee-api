import httpx

from linguee_api.downloaders.interfaces import DownloaderError, IDownloader


class HTTPXDownloader(IDownloader):
    """
    Real downloader.

    Sends request to linguee.com to read the page.
    """

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
