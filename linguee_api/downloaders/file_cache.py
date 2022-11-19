import pathlib
import urllib.parse
from typing import Optional

from linguee_api.downloaders.interfaces import ICache, IDownloader


class FileCache(ICache):
    """File Cache."""

    def __init__(self, cache_directory: pathlib.Path, upstream: IDownloader):
        self.cache_directory = cache_directory
        self.upstream = upstream
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    async def get_from_cache(self, url: str) -> Optional[str]:
        page_file = self._get_page_file(url)
        if page_file.is_file():
            return page_file.read_text(encoding="utf-8")
        return None

    async def put_to_cache(self, url: str, page: str) -> None:
        page_file = self._get_page_file(url)
        page_file.write_text(page, encoding="utf-8")

    def _get_page_file(self, url: str) -> pathlib.Path:
        return self.cache_directory / urllib.parse.quote(url, safe="")
