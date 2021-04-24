import abc
import pathlib

import httpx
from furl import furl

from linguee_api.utils import read_text

DEFAULT_EXAMPLES_DIRECTORY = pathlib.Path(__file__).parents[1] / "examples"


class DownloaderError(Exception):
    pass


class IDownloader(abc.ABC):
    @abc.abstractmethod
    async def download(self, url: str) -> str:
        """Download a page or raise an exception"""
        ...


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


class MemoryCache(IDownloader):
    """
    Memory cache.

    Exposes the downloader interface, but requires the upstream to work and
    keeps records in memory.
    """

    def __init__(self, upstream: IDownloader):
        self.upstream = upstream
        self.cache: dict[str, str] = {}

    async def download(self, url: str) -> str:
        if url not in self.cache:
            self.cache[url] = await self.upstream.download(url)
        return self.cache[url]


class ExampleDownloader(IDownloader):
    """
    Fake downloader.

    Reads data from "examples" directory.
    """

    def __init__(self, examples_directory: pathlib.Path = DEFAULT_EXAMPLES_DIRECTORY):
        self.examples_directory = examples_directory
        if not self.examples_directory.is_dir():
            raise RuntimeError(f"Directory {self.examples_directory} not found")

    async def download(self, url: str) -> str:
        parsed_url = furl(url)
        query = parsed_url.args["query"]
        response_file = self.examples_directory / f"{query}.html"
        if not response_file.is_file():
            raise DownloaderError(f"Example for {query} not found")
        return read_text(response_file)
