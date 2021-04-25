import pathlib
import urllib.parse

from linguee_api.downloaders.interfaces import IDownloader
from linguee_api.utils import read_text


class FileCache(IDownloader):
    """File Cache."""

    def __init__(self, cache_directory: pathlib.Path, upstream: IDownloader):
        self.cache_directory = cache_directory
        self.upstream = upstream
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    async def download(self, url: str) -> str:
        page_file = self.get_page_file(url)
        if not page_file.is_file():
            page = await self.upstream.download(url)
            page_file.write_text(page)
        return read_text(page_file)

    def get_page_file(self, url: str) -> pathlib.Path:
        return self.cache_directory / urllib.parse.quote(url, safe="")
