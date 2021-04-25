import pytest

from linguee_api.downloaders.file_cache import FileCache
from linguee_api.linguee_client import get_autocompletions_url
from linguee_api.models import Autocompletions
from linguee_api.parsers import XExtractParser


@pytest.mark.asyncio
async def test_parse_autocompletions_should_return_autocompletions(
    examples_downloader: FileCache,
):
    url = get_autocompletions_url(query="katz", src="de", dst="en")
    page = await examples_downloader.download(url)
    parser = XExtractParser()
    parse_result = parser.parse_autocompletions(page)

    a = Autocompletions.AutocompletionItem
    t = Autocompletions.AutocompletionItem.TranslationItem
    first_item = a(
        text="Katze",
        pos="f",
        translations=[
            t(text="cat", pos="n"),
            t(text="feline", pos="n"),
            t(text="crab", pos="n"),
        ],
    )
    assert parse_result.autocompletions[0] == first_item
