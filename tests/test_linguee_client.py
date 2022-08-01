import pytest

from linguee_api.const import LANGUAGE_CODE, LANGUAGES
from linguee_api.linguee_client import LingueeClient
from linguee_api.models import FollowCorrections, ParseError, SearchResult


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "follow_corrections",
    [
        FollowCorrections.ALWAYS,
        FollowCorrections.ON_EMPTY_TRANSLATIONS,
    ],
)
async def test_linguee_client_should_redirect_on_not_found(
    linguee_client: LingueeClient,
    follow_corrections,
):
    search_result = await linguee_client.process_search_result(
        query="constibado",
        src="pt",
        dst="en",
        guess_direction=False,
        follow_corrections=follow_corrections,
    )
    assert search_result.query == "constipado"


@pytest.mark.asyncio
async def test_linguee_client_should_not_redirect_if_not_asked(
    linguee_client: LingueeClient,
):
    search_result = await linguee_client.process_search_result(
        query="constibado",
        src="pt",
        dst="en",
        guess_direction=False,
        follow_corrections=FollowCorrections.NEVER,
    )
    assert isinstance(search_result, ParseError)
    assert search_result.message == "Translation not found"


@pytest.mark.asyncio
@pytest.mark.parametrize("lang", list(LANGUAGES.keys()))
async def test_linguee_client_should_process_test_requests(
    linguee_client: LingueeClient,
    lang: LANGUAGE_CODE,
):
    search_result = await linguee_client.process_search_result(
        query="test",
        src="en",
        dst=lang,
        guess_direction=False,
        follow_corrections=FollowCorrections.ALWAYS,
    )
    assert isinstance(search_result, SearchResult)
