from typing import Optional

import pytest

from linguee_api.const import LANGUAGE_CODE
from linguee_api.downloaders.file_cache import FileCache
from linguee_api.linguee_client import get_search_url
from linguee_api.parsers import XExtractParser


@pytest.mark.parametrize(
    ["query", "src", "dst", "is_not_found"],
    [
        ("constibado", "pt", "en", True),
        ("esgotar", "pt", "en", False),
        ("not bad", "en", "pt", False),
        ("xxxxzzzz", "pt", "en", True),
    ],
)
@pytest.mark.asyncio
async def test_parser_should_detect_not_found(
    examples_downloader: FileCache,
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    is_not_found: bool,
):
    url = get_search_url(query=query, src=src, dst=dst, guess_direction=False)
    page = await examples_downloader.download(url)
    assert XExtractParser().is_not_found(page) == is_not_found


@pytest.mark.parametrize(
    ["query", "correction"],
    [
        ("constibado", "constipado"),
        ("esgotar", None),
        ("xxxxzzzz", None),
    ],
)
@pytest.mark.asyncio
async def test_parser_should_find_correction(
    examples_downloader: FileCache, query: str, correction: Optional[str]
):
    url = get_search_url(query=query, src="pt", dst="en", guess_direction=False)
    page = await examples_downloader.download(url)
    assert XExtractParser().find_correction(page) == correction


@pytest.mark.parametrize(
    ["query", "src", "dst"],
    [
        ("esgotar", "pt", "en"),
        ("obrigado", "pt", "en"),
        ("not bad", "en", "pt"),
    ],
)
@pytest.mark.asyncio
async def test_parse_to_dict_should_return_parseable_result(
    examples_downloader: FileCache,
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
):
    url = get_search_url(query=query, src=src, dst=dst, guess_direction=False)
    page = await examples_downloader.download(url)
    XExtractParser().parse_search_result_to_page(page)
