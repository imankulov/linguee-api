import abc


class DownloaderError(Exception):
    pass


class IDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, url: str) -> str:
        """Download a page or raise an exception"""
        ...
