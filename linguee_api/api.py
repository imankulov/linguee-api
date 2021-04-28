import sentry_sdk
from fastapi import FastAPI, Response, status
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.responses import RedirectResponse

from linguee_api.config import settings
from linguee_api.const import LANGUAGE_CODE, PROJECT_DESCRIPTION
from linguee_api.downloaders.file_cache import FileCache
from linguee_api.downloaders.httpx_downloader import HTTPXDownloader
from linguee_api.downloaders.memory_cache import MemoryCache
from linguee_api.linguee_client import LingueeClient
from linguee_api.models import Autocompletions, ParseError, SearchResult
from linguee_api.parsers import XExtractParser

sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.sentry_environment)
app = FastAPI(
    title="Linguee API",
    description=PROJECT_DESCRIPTION,
    version="2.0.0",
)
app.add_middleware(SentryAsgiMiddleware)

page_downloader = MemoryCache(
    upstream=FileCache(
        cache_directory=settings.cache_directory, upstream=HTTPXDownloader()
    )
)
client = LingueeClient(page_downloader=page_downloader, page_parser=XExtractParser())


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/docs")


@app.get(
    "/api/v2/translations",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[SearchResult.Lemma]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def translations(
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    response: Response,
    guess_direction: bool = False,
):
    """
    Translate the query between src and dst language.

    The response contains the list of lemma objects matching the query in the source
    language. Each of these lemmas is annotated with one or multiple translations
    and optional examples.
    """
    result = await client.process_search_result(
        query=query,
        src=src,
        dst=dst,
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
        status.HTTP_200_OK: {"model": list[SearchResult.Example]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def examples(
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    response: Response,
    guess_direction: bool = False,
):
    """Provide translation examples."""
    result = await client.process_search_result(
        query=query,
        src=src,
        dst=dst,
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
        status.HTTP_200_OK: {"model": list[SearchResult.ExternalSource]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def external_sources(
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    response: Response,
    guess_direction: bool = False,
):
    """Provide translation examples from external (unverified) sources."""
    result = await client.process_search_result(
        query=query,
        src=src,
        dst=dst,
        guess_direction=guess_direction,
    )
    if isinstance(result, ParseError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result
    return result.external_sources


@app.get(
    "/api/v2/autocompletions",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": list[Autocompletions.AutocompletionItem]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ParseError},
    },
)
async def autocompletions(
    query: str,
    src: LANGUAGE_CODE,
    dst: LANGUAGE_CODE,
    response: Response,
):
    """Provide translation examples from external (unverified) sources."""
    result = await client.process_autocompletions(
        query=query,
        src_lang_code=src,
        dst_lang_code=dst,
    )
    if isinstance(result, ParseError):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return result
    return result.autocompletions
