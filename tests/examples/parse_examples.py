#!/usr/bin/env python
import json
import pathlib

import chardet
import click

from linguee_api.parsers import XExtractParser

examples = [
    "not_bad.html",
    "esgotar.html",
    "not_bad.html",
]


@click.command()
def parse_examples():
    for example in examples:
        parse_page(example)


def parse_page(filename_html: str):
    page_html = read_text(pathlib.Path(filename_html))
    page_json = XExtractParser().parse_to_dict(page_html)
    filename_json = filename_html.replace(".html", ".json")
    pathlib.Path(filename_json).write_text(
        json.dumps(page_json, indent=2, ensure_ascii=False)
    )


def read_text(path: pathlib.Path) -> str:
    content = path.read_bytes()
    encoding = chardet.detect(content)["encoding"]
    return content.decode(encoding)


if __name__ == "__main__":
    parse_examples()
