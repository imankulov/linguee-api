import pytest

from linguee_api.const import LANGUAGE_CODE, LANGUAGES
from linguee_api.linguee_client import LingueeClient
from linguee_api.models import SearchResult


@pytest.mark.asyncio
async def test_linguee_client_should_redirect_on_not_found(
    linguee_client: LingueeClient,
):
    search_result = await linguee_client.process_search_result(
        query="constibado", src="pt", dst="en", guess_direction=False
    )
    assert search_result.query == "constipado"


@pytest.mark.asyncio
@pytest.mark.parametrize("lang", list(LANGUAGES.keys()))
async def test_linguee_client_should_process_test_requests(
    linguee_client: LingueeClient,
    lang: LANGUAGE_CODE,
):
    search_result = await linguee_client.process_search_result(
        query="test", src="en", dst=lang, guess_direction=False
    )
    assert isinstance(search_result, SearchResult)
