from typing import Union
from urllib.parse import urlencode

from linguee_api.const import LANGUAGES, MAX_REDIRECTS, LanguageCode
from linguee_api.downloaders import DownloaderError, IDownloader
from linguee_api.parsers import IParser
from linguee_api.schema import LingueeCorrection, LingueePage, ParseError


class LingueeClient:
    """Linguee client. The core class of the application."""

    def __init__(
        self,
        *,
        page_downloader: IDownloader,
        page_parser: IParser,
        max_redirects=MAX_REDIRECTS,
    ):
        self.page_downloader = page_downloader
        self.page_parser = page_parser
        self.max_redirects = max_redirects

    async def process(
        self,
        *,
        query: str,
        src_lang_code: LanguageCode,
        dst_lang_code: LanguageCode,
        guess_direction: bool,
    ) -> Union[LingueePage, ParseError]:
        url = get_linguee_url(
            query=query,
            src_lang_code=src_lang_code,
            dst_lang_code=dst_lang_code,
            guess_direction=guess_direction,
        )

        for i in range(self.max_redirects):
            try:
                page_html = await self.page_downloader.download(url)
            except DownloaderError as error:
                return ParseError(message=str(error))

            parse_result = self.page_parser.parse(page_html)
            if isinstance(parse_result, ParseError):
                return parse_result
            elif isinstance(parse_result, LingueeCorrection):
                url = get_linguee_url(
                    query=parse_result.correction,
                    src_lang_code=src_lang_code,
                    dst_lang_code=dst_lang_code,
                    guess_direction=guess_direction,
                )
            elif isinstance(parse_result, LingueePage):
                return parse_result
            else:
                raise RuntimeError(f"Unexpected API result: {parse_result}")

        return ParseError(
            message=f"Still redirecting after {self.max_redirects} redirects"
        )


def get_linguee_url(
    *,
    query: str,
    src_lang_code: LanguageCode,
    dst_lang_code: LanguageCode,
    guess_direction: bool,
):
    """
    Return a Linguee URL.
    """
    src_lang_name = LANGUAGES[src_lang_code]
    dst_lang_name = LANGUAGES[dst_lang_code]
    url = f"https://www.linguee.com/{src_lang_name}-{dst_lang_name}/search"
    query_params = {
        "query": query,
        "ajax": "1",
    }
    if not guess_direction:
        query_params["source"] = src_lang_code.upper()
    return f"{url}?{urlencode(query_params)}"
