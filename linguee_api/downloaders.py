import abc
import pathlib

import httpx
from furl import furl

from linguee_api.utils import read_text

DEFAULT_EXAMPLES_DIRECTORY = pathlib.Path(__file__).parents[1] / "tests" / "examples"


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


class ExampleDownloader(IDownloader):
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
