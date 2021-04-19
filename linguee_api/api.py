from fastapi import FastAPI, Response, status

from linguee_api.api_client import APIClient
from linguee_api.const import LanguageCode
from linguee_api.downloaders import HTTPXDownloader
from linguee_api.parsers import XExtractParser
from linguee_api.schema import LingueePage, ParseError

app = FastAPI()
client = APIClient(page_downloader=HTTPXDownloader(), page_parser=XExtractParser())


@app.get(
    "/translate",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[LingueePage.Lemma]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def translate(
    query: str,
    src: LanguageCode,
    dst: LanguageCode,
    guess_direction: bool,
    response: Response,
):
    """
    Translate the query between src and dst language.

    The response contains the list of lemma objects matching the query in the source
    language. Each of these lemmas is annotated with one or multiple translations
    and optional examples.
    """
    result = await client.process(
        query=query,
        src_lang_code=src,
        dst_lang_code=dst,
        guess_direction=guess_direction,
    )
    if isinstance(result, ParseError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result
    return result.lemmas


@app.get(
    "/examples",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[LingueePage.Example]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def examples(
    query: str,
    src: LanguageCode,
    dst: LanguageCode,
    guess_direction: bool,
    response: Response,
):
    """Provide translation examples."""
    result = await client.process(
        query=query,
        src_lang_code=src,
        dst_lang_code=dst,
        guess_direction=guess_direction,
    )
    if isinstance(result, ParseError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result
    return result.examples


@app.get(
    "/external_sources",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[LingueePage.ExternalSource]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def external_sources(
    query: str,
    src: LanguageCode,
    dst: LanguageCode,
    guess_direction: bool,
    response: Response,
):
    """Provide translation examples from external (unverified) sources."""
    result = await client.process(
        query=query,
        src_lang_code=src,
        dst_lang_code=dst,
        guess_direction=guess_direction,
    )
    if isinstance(result, ParseError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result
    return result.external_sources
