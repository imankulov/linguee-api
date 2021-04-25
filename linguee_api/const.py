import pathlib
from typing import Literal

PROJECT_ROOT = pathlib.Path(__file__).parents[1]
USER_AGENT = "Linguee API proxy (https://github.com/imankulov/linguee-api)"
LANGUAGE_CODE = Literal[
    "bg",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fi",
    "fr",
    "hu",
    "it",
    "ja",
    "lt",
    "lv",
    "mt",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sv",
    "zh",
]
LANGUAGES = {
    "bg": "bulgarian",
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "fi": "finnish",
    "fr": "french",
    "hu": "hungarian",
    "it": "italian",
    "ja": "japanese",
    "lt": "lithuanian",
    "lv": "latvian",
    "mt": "maltese",
    "nl": "dutch",
    "pl": "polish",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sk": "slovak",
    "sl": "slovene",
    "sv": "swedish",
    "zh": "chinese",
}
MAX_REDIRECTS = 5
PROJECT_DESCRIPTION = """
<p>
    <a href="https://linguee.com" target="_blank">Linguee</a> provides excellent
    dictionary and translation memory service. Unfortunately, there is no way you
    can get automated access to it. Linguee API fixes the problem. It acts as a
    proxy and converts their HTML responses to easy-to-use JSON API.
</p>
<p>
    This installation is an example. If you want to have reliable service, install
    it yourself. The source code and installation instructions are available at
    <a href="https://github.com/imankulov/linguee-api"
    >github.com/imankulov/linguee-api</a>.
</p>
<p>
    For any questions, ideas or bug reports, fill in
    <a href="https://github.com/imankulov/linguee-api/issues" target="_blank">
    the issue at GitHub</a>.
</p>
"""
