#!/usr/bin/env python
import asyncio
import pathlib

import click
from asgiref.sync import async_to_sync

from linguee_api.downloaders.file_cache import FileCache
from linguee_api.downloaders.httpx_downloader import HTTPXDownloader
from linguee_api.linguee_client import get_autocompletions_url, get_search_url

download_urls = [
    get_search_url(query="constibado", src="pt", dst="en", guess_direction=False),
    get_search_url(query="esgotar", src="pt", dst="en", guess_direction=False),
    get_search_url(query="obrigado", src="pt", dst="en", guess_direction=False),
    get_search_url(query="xxxxzzzz", src="pt", dst="en", guess_direction=False),
    get_search_url(query="not bad", src="en", dst="pt", guess_direction=False),
    get_autocompletions_url(query="katz", src="de", dst="en"),
]


examples_root = pathlib.Path(__file__).parents[1] / "examples"
downloader = FileCache(cache_directory=examples_root, upstream=HTTPXDownloader())


@click.group()
def cli():
    pass


@cli.command()
def download():
    async_to_sync(run_downloader)()


async def run_downloader():
    tasks = [downloader.download(url) for url in download_urls]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    cli()
