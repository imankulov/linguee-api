from typing import Union
from urllib.parse import urlencode

from loguru import logger

from linguee_api.const import LANGUAGE_CODE, LANGUAGES, MAX_REDIRECTS
from linguee_api.downloaders.interfaces import DownloaderError, IDownloader
from linguee_api.models import (
    Autocompletions,
    AutocompletionsOrError,
    Correction,
    ParseError,
    SearchResult,
)
from linguee_api.parsers import IParser


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

    async def process_search_result(
        self,
        *,
        query: str,
        src: LANGUAGE_CODE,
        dst: LANGUAGE_CODE,
        guess_direction: bool,
    ) -> Union[SearchResult, ParseError]:
        logger.info(
            f"Processing API request: {query=}, {src=}, {dst=}, {guess_direction=}"
        )
        url = get_search_url(
            query=query,
            src=src,
            dst=dst,
            guess_direction=guess_direction,
        )

        for i in range(self.max_redirects):
            try:
                page_html = await self.page_downloader.download(url)
            except DownloaderError as error:
                logger.error(f"Error downloading URL: {error=}, {url=}")
                return ParseError(message=str(error))

            parse_result = self.page_parser.parse_search_result(page_html)
            if isinstance(parse_result, ParseError):
                logger.info(f"Parser returned parse error: {parse_result=}")
                return parse_result
            elif isinstance(parse_result, Correction):
                logger.info(f"Parser returned correction: {parse_result=}")
                url = get_search_url(
                    query=parse_result.correction,
                    src=src,
                    dst=dst,
                    guess_direction=guess_direction,
                )
            elif isinstance(parse_result, SearchResult):
                logger.info(
                    f"Parser returned search result: "
                    f"{parse_result.query=}, "
                    f"{len(parse_result.lemmas)=}, "
                    f"{len(parse_result.examples)=}, "
                    f"{len(parse_result.external_sources)=}"
                )
                return parse_result
            else:
                logger.error(f"Unexpected API result: {parse_result=}")
                raise RuntimeError(f"Unexpected API result: {parse_result}")

        still_redirecting = f"Still redirecting after {self.max_redirects} redirects"
        logger.error(still_redirecting)
        return ParseError(message=still_redirecting)

    async def process_autocompletions(
        self,
        *,
        query: str,
        src_lang_code: LANGUAGE_CODE,
        dst_lang_code: LANGUAGE_CODE,
    ) -> AutocompletionsOrError:
        url = get_autocompletions_url(
            query=query,
            src=src_lang_code,
            dst=dst_lang_code,
        )
        try:
            page_html = await self.page_downloader.download(url)
        except DownloaderError as error:
            return ParseError(message=str(error))

        parse_result = self.page_parser.parse_autocompletions(page_html)
        if isinstance(parse_result, ParseError):
            return parse_result
        elif isinstance(parse_result, Autocompletions):
            return parse_result

        raise RuntimeError(f"Unexpected API result: {parse_result}")


def get_search_url(
    *,
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    guess_direction: bool,
):
    """
    Return a Linguee URL.
    """
    src_lang_name = LANGUAGES[src]
    dst_lang_name = LANGUAGES[dst]
    url = f"https://www.linguee.com/{src_lang_name}-{dst_lang_name}/search"
    query_params = {
        "query": query,
        "ajax": "1",
    }
    if not guess_direction:
        query_params["source"] = src.upper()
    return f"{url}?{urlencode(query_params)}"


def get_autocompletions_url(
    *,
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
):
    """Return a URL for auto-completions."""
    src_lang_name = LANGUAGES[src]
    dst_lang_name = LANGUAGES[dst]
    url = f"https://www.linguee.com/{src_lang_name}-{dst_lang_name}/search"
    query_params = {
        "qe": query,
    }
    return f"{url}?{urlencode(query_params)}"
