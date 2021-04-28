import pytest

from linguee_api.linguee_client import LingueeClient


@pytest.mark.asyncio
async def test_linguee_client_should_redirect_on_not_found(
    linguee_client: LingueeClient,
):
    search_result = await linguee_client.process_search_result(
        query="constibado", src="pt", dst="en", guess_direction=False
    )
    assert search_result.query == "constipado"
