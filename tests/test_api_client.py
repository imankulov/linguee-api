from linguee_api.linguee_client import get_linguee_url


def test_get_linguee_url_should_return_valid_url():
    url = get_linguee_url(
        query="bacalhau", src_lang_code="pt", dst_lang_code="en", guess_direction=False
    )
    assert url == (
        "https://www.linguee.com/portuguese-english/search?"
        "query=bacalhau&ajax=1&source=PT"
    )
