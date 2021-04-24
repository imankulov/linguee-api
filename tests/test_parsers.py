import json
import pathlib
from typing import Optional

import pytest

from linguee_api.parsers import XExtractParser
from linguee_api.utils import read_text


@pytest.fixture
def examples_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parents[1] / "examples"


@pytest.mark.parametrize(
    ["filename", "is_not_found"],
    [
        ("constibado.html", True),
        ("esgotar.html", False),
        ("not_bad.html", False),
        ("xxxxzzzz.html", True),
    ],
)
def test_parser_should_detect_not_found(
    examples_dir: pathlib.Path, filename: str, is_not_found: bool
):
    page = read_text(examples_dir / filename)
    assert XExtractParser().is_not_found(page) == is_not_found


@pytest.mark.parametrize(
    ["filename", "correction"],
    [
        ("constibado.html", "constipado"),
        ("esgotar.html", None),
        ("not_bad.html", None),
        ("xxxxzzzz.html", None),
    ],
)
def test_parser_should_find_correction(
    examples_dir: pathlib.Path, filename: str, correction: Optional[str]
):
    page = read_text(examples_dir / filename)
    assert XExtractParser().find_correction(page) == correction


@pytest.mark.parametrize(
    ["filename_html", "filename_json"],
    [
        ("esgotar.html", "esgotar.json"),
        ("obrigado.html", "obrigado.json"),
        ("not_bad.html", "not_bad.json"),
    ],
)
def test_parse_to_dict_should_return_expected_datastructure(
    examples_dir: pathlib.Path, filename_html: str, filename_json: str
):
    page_html = read_text(examples_dir / filename_html)
    parsed_result = XExtractParser().parse_to_dict(page_html)

    page_json = json.loads((examples_dir / filename_json).read_text())
    assert parsed_result == page_json


@pytest.mark.parametrize(
    "filename_html",
    [
        "esgotar.html",
        "obrigado.html",
        "not_bad.html",
    ],
)
def test_parse_to_dict_should_return_parseable_result(
    examples_dir: pathlib.Path, filename_html: str
):
    page_html = read_text(examples_dir / filename_html)
    XExtractParser().parse_to_page(page_html)
