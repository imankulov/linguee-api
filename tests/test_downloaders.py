import random
import string

import pytest

from linguee_api.downloaders.httpx_downloader import HTTPXDownloader
from linguee_api.downloaders.interfaces import DownloaderError


@pytest.mark.asyncio
async def test_httpx_downloader_should_download_a_page():
    url = (
        "https://www.linguee.com/portuguese-english/search?"
        "query=bacalhau&ajax=1&source=PT"
    )
    content = await HTTPXDownloader().download(url)
    assert "bacalhau" in content


@pytest.mark.asyncio
async def test_httpx_downloader_should_raise_exception_on_invalid_domain_name():
    random_sequence = "".join(random.choices(string.ascii_lowercase, k=30))
    invalid_url = f"https://{random_sequence}.com"
    with pytest.raises(DownloaderError):
        await HTTPXDownloader().download(invalid_url)


@pytest.mark.asyncio
async def test_httpx_downloader_should_raise_exception_on_non200_code():
    invalid_url = "https://httpbin.org/status/403"
    with pytest.raises(DownloaderError):
        await HTTPXDownloader().download(invalid_url)
