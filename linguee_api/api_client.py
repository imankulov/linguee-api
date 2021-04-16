from urllib.parse import urlencode

from linguee_api.downloaders import IDownloader
from linguee_api.parsers import IParser
from linguee_api.schema import LingueeCorrection, LingueePage, ParseError

USER_AGENT = "Linguee API proxy (https://github.com/imankulov/linguee-api)"

LANGUAGES = {
    "BG": "bulgarian",
    "CS": "czech",
    "DA": "danish",
    "DE": "german",
    "EL": "greek",
    "EN": "english",
    "ES": "spanish",
    "ET": "estonian",
    "FI": "finnish",
    "FR": "french",
    "HU": "hungarian",
    "IT": "italian",
    "JA": "japanese",
    "LT": "lithuanian",
    "LV": "latvian",
    "MT": "maltese",
    "NL": "dutch",
    "PL": "polish",
    "PT": "portuguese",
    "RO": "romanian",
    "RU": "russian",
    "SK": "slovak",
    "SL": "slovene",
    "SV": "swedish",
    "ZH": "chinese",
}

MAX_REDIRECTS = 5


class APIClient:
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
        src_lang_code: str,
        dst_lang_code: str,
        guess_direction: bool,
    ):
        url = get_linguee_url(
            query=query,
            src_lang_code=src_lang_code,
            dst_lang_code=dst_lang_code,
            guess_direction=guess_direction,
        )

        for i in range(self.max_redirects):
            page_html = await self.page_downloader.download(url)
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
                return LingueePage
            else:
                raise RuntimeError("Unexpected API result.")

        return ParseError(
            message=f"Still redirecting after {self.max_redirects} redirects"
        )


def get_linguee_url(
    *,
    query: str,
    src_lang_code: str,
    dst_lang_code: str,
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
        query_params["source"] = src_lang_code
    return f"{url}?{urlencode(query_params)}"
