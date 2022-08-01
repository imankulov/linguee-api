from typing import Optional

import pytest

from linguee_api.const import LANGUAGE_CODE
from linguee_api.downloaders.file_cache import FileCache
from linguee_api.linguee_client import get_search_url
from linguee_api.models import UsageFrequency
from linguee_api.parsers import XExtractParser


@pytest.mark.parametrize(
    ["query", "src", "dst", "is_not_found"],
    [
        ("constibado", "pt", "en", True),
        ("Möglichkei", "de", "en", False),  # At least, there are examples
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


@pytest.mark.asyncio
async def test_parser_should_find_translation_examples(
    examples_downloader: FileCache,
):
    url = get_search_url(query="obrigado", src="pt", dst="en", guess_direction=False)
    page_html = await examples_downloader.download(url)
    page = XExtractParser().parse_search_result_to_page(page_html)
    examples_of_1st_translation = page.lemmas[0].translations[0].examples
    assert examples_of_1st_translation is not None
    assert len(examples_of_1st_translation) == 1
    assert examples_of_1st_translation[0].src == (
        "Obrigado por sua participação em nossa pesquisa."
    )
    assert examples_of_1st_translation[0].dst == (
        "Thank you for your participation in our survey."
    )


@pytest.mark.parametrize(
    ["query", "src", "dst", "correction"],
    [
        ("constibado", "pt", "en", "constipado"),
        (
            "Möglichkei",
            "de",
            "en",
            "möglichkeit",
        ),  # Despite having examples, Linguee provides a correction.
        ("esgotar", "pt", "en", None),
        ("xxxxzzzz", "pt", "en", None),
    ],
)
@pytest.mark.asyncio
async def test_parser_should_find_correction(
    examples_downloader: FileCache,
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    correction: Optional[str],
):
    url = get_search_url(query=query, src=src, dst=dst, guess_direction=False)
    page = await examples_downloader.download(url)
    assert XExtractParser().find_correction(page) == correction


@pytest.mark.parametrize(
    ["query", "src", "dst"],
    [
        ("esgotar", "pt", "en"),
        (
            "Möglichkei",
            "de",
            "en",
        ),  # The page only has external sources
        ("obrigado", "pt", "en"),
        ("not bad", "en", "pt"),
        ("einfach", "de", "en"),
        ("Tisch", "de", "en"),
        ("wünschen", "de", "en"),
        ("envisage", "en", "zh"),
        ("envisage", "en", "sv"),
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


@pytest.mark.asyncio
async def test_parser_should_find_grammar_info_in_german_verbs(
    examples_downloader: FileCache,
):
    url = get_search_url(query="bringen", src="de", dst="en", guess_direction=False)
    page_html = await examples_downloader.download(url)
    page = XExtractParser().parse_search_result_to_page(page_html)
    assert page.lemmas[0].grammar_info == "Akk"


@pytest.mark.asyncio
async def test_parser_should_process_examples_without_links(
    examples_downloader: FileCache,
):
    url = get_search_url(query="einfach", src="de", dst="en", guess_direction=False)
    page_html = await examples_downloader.download(url)
    page = XExtractParser().parse_search_result_to_page(page_html)
    sources = page.external_sources
    assert all([s.src_url.startswith("http") for s in sources])
    assert all([s.dst_url.startswith("http") for s in sources])


@pytest.mark.asyncio
async def test_parser_should_find_almost_always_usage_frequency(
    examples_downloader: FileCache,
):
    url = get_search_url(query="bacalhau", src="pt", dst="en", guess_direction=False)
    page_html = await examples_downloader.download(url)
    page = XExtractParser().parse_search_result_to_page(page_html)
    assert page.lemmas[0].translations[1].usage_frequency is None
    assert (
        page.lemmas[0].translations[0].usage_frequency == UsageFrequency.ALMOST_ALWAYS
    )


@pytest.mark.asyncio
async def test_parser_should_find_often_usage_frequency(
    examples_downloader: FileCache,
):
    url = get_search_url(query="placa", src="pt", dst="en", guess_direction=False)
    page_html = await examples_downloader.download(url)
    page = XExtractParser().parse_search_result_to_page(page_html)
    assert page.lemmas[0].translations[1].usage_frequency is None
    assert page.lemmas[0].translations[0].usage_frequency == UsageFrequency.OFTEN
