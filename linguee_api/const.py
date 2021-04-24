from typing import Literal

USER_AGENT = "Linguee API proxy (https://github.com/imankulov/linguee-api)"
LanguageCode = Literal[
    "BG",
    "CS",
    "DA",
    "DE",
    "EL",
    "EN",
    "ES",
    "ET",
    "FI",
    "FR",
    "HU",
    "IT",
    "JA",
    "LT",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "RU",
    "SK",
    "SL",
    "SV",
    "ZH",
]
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
