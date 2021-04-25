from linguee_api.linguee_client import get_search_url


def test_get_linguee_url_should_return_valid_url():
    url = get_search_url(query="bacalhau", src="pt", dst="en", guess_direction=False)
    assert url == (
        "https://www.linguee.com/portuguese-english/search?"
        "query=bacalhau&ajax=1&source=PT"
    )
