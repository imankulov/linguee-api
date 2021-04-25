from linguee_api.downloaders.interfaces import DownloaderError, IDownloader


class ErrorDownloader(IDownloader):
    """
    A downloader that always raises an DownloaderError.

    Helpful to use as the upstream downloader for FileCache() in tests to make sure
    that we don't send requests to the server.
    """

    async def download(self, url: str) -> str:
        raise DownloaderError(f"I cannot download {url}")
