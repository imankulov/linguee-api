import sentry_sdk
from fastapi import FastAPI, Response, status
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.responses import RedirectResponse

from linguee_api.const import PROJECT_DESCRIPTION, LanguageCode
from linguee_api.downloaders import HTTPXDownloader, MemoryCache
from linguee_api.linguee_client import LingueeClient
from linguee_api.parsers import XExtractParser
from linguee_api.schema import LingueePage, ParseError

sentry_sdk.init()

app = FastAPI(
    title="Linguee API",
    description=PROJECT_DESCRIPTION,
    version="2.0.0",
)
app.add_middleware(SentryAsgiMiddleware)

page_downloader = MemoryCache(upstream=HTTPXDownloader())
client = LingueeClient(page_downloader=page_downloader, page_parser=XExtractParser())


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/docs")


@app.get(
    "/api/v2/translations",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[LingueePage.Lemma]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def translations(
    query: str,
    src: LanguageCode,
    dst: LanguageCode,
    response: Response,
    guess_direction: bool = False,
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
    "/api/v2/examples",
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
    response: Response,
    guess_direction: bool = False,
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
    "/api/v2/external_sources",
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
    response: Response,
    guess_direction: bool = False,
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
