import abc
from typing import Dict, List, Optional

from xextract import Group, String

from linguee_api.models import (
    Autocompletions,
    AutocompletionsOrError,
    Correction,
    NotFound,
    SearchResult,
    SearchResultOrError,
    UsageFrequency,
)
from linguee_api.parser_utils import concat_values, normalize, take_first_item


class IParser(abc.ABC):
    @abc.abstractmethod
    def parse_search_result(self, page_html: str) -> SearchResultOrError:
        ...

    @abc.abstractmethod
    def parse_autocompletions(self, page_html: str) -> AutocompletionsOrError:
        ...


class XExtractParser(IParser):
    def parse_search_result(self, page_html: str) -> SearchResultOrError:
        # check if the page is correction
        correction = self.find_correction(page_html)
        if correction:
            return Correction(correction=correction)
        # check if the page is a not found page without any correction
        if self.is_not_found(page_html):
            return NotFound()
        # assume it's a valid result
        return self.parse_search_result_to_page(page_html)

    def is_not_found(self, page_html: str) -> bool:
        """Return True if the page is a NOT FOUND page."""
        return String(css="h1.noresults").parse(page_html) != []

    def find_correction(self, page_html: str) -> Optional[str]:
        """Find the correction for a NOT FOUND page."""
        corrections = String(css="span.corrected").parse(page_html)
        if corrections:
            return corrections[0]
        return None

    def parse_search_result_to_page(self, page_html: str) -> SearchResult:
        parsed_result = self.parse_search_result_to_dict(page_html)
        return SearchResult(**parsed_result)

    def parse_search_result_to_dict(self, page_html: str) -> dict:
        return search_result_schema.parse(page_html)

    def parse_autocompletions(self, page_html: str) -> AutocompletionsOrError:
        parsed_result = self.parse_autocompletions_to_dict(page_html)
        return Autocompletions(**parsed_result)

    def parse_autocompletions_to_dict(self, page_html: str) -> dict:
        return autocompletions_schema.parse(page_html)


def is_featured(classname):
    return "featured" in classname


def normalize_example(text):
    """
    Normalize the text in the example.

    Same as normalize(), but remove the last two words, which are the links to the
    source website.
    """
    text = normalize(text)
    text = " ".join(text.split()[:-2])
    return text


def parse_audio_links(text: Optional[str]) -> List[Dict[str, str]]:
    if not text:
        return []

    chunks = [chunk.strip('");') for chunk in text.split(",")]
    if not chunks:
        return []

    ret = []
    for i in range(1, len(chunks), 2):
        url_part = chunks[i]
        lang = chunks[i + 1]
        url = f"https://www.linguee.com/mp3/{url_part}.mp3"
        ret.append({"url": url, "lang": lang})
    return ret


def parse_usage_frequency(text: Optional[str]) -> Optional[UsageFrequency]:
    if not text:
        return None
    chunks = set(text.strip().split())
    if "usedveryoften" in chunks:
        return UsageFrequency.OFTEN
    if "usedalmostalways" in chunks:
        return UsageFrequency.ALMOST_ALWAYS
    return None


def normalize_lemma_text(children):
    return " ".join(children["item"])


lemma_schema = [
    String(
        name="featured",
        xpath="self::*",
        attr="class",
        quant=1,
        callback=is_featured,
    ),
    # We parse text as a group, because the lemma may have one or more elements, all
    # of them represented with "a.dictLink". In most cases it's just a single element,
    # but if it's more, we need to collect then all, and merge them together in the
    # group callback normalize_lemma_text()
    Group(
        name="text",
        quant=1,
        css="span.tag_lemma",
        callback=normalize_lemma_text,
        children=[
            String(
                name="item",
                css="a.dictLink",
                quant="+",
                callback=normalize,
            ),
        ],
    ),
    concat_values(
        "pos",
        String(
            name="pos",
            css="span.tag_lemma > span.tag_wordtype, span.tag_lemma > span.tag_type",
            quant="*",
        ),
    ),
    # We parse text as a group, because grammar_info may have zero or more elements.
    # and we care about the first record only
    Group(
        name="grammar_info",
        quant=1,
        callback=take_first_item,
        children=[
            String(
                name="item",
                quant="*",
                callback=normalize,
                css=(
                    "span.tag_lemma > span.tag_lemma_context > "
                    "span.placeholder > span.grammar_info"
                ),
            )
        ],
    ),
    String(
        name="audio_links",
        quant="?",
        css="span.tag_lemma > a.audio",
        attr="onclick",
        callback=parse_audio_links,
    ),
    Group(
        name="translations",
        css="div.translation_lines div.translation",
        quant="+",
        children=[
            String(
                name="featured",
                xpath="self::*",
                attr="class",
                quant=1,
                callback=is_featured,
            ),
            String(
                name="text",
                css="a.dictLink",
                quant=1,
                callback=normalize,
            ),
            concat_values(
                "pos",
                String(
                    name="pos",
                    css="span.tag_type",
                    quant="*",
                    attr="title",
                ),
            ),
            String(
                name="audio_links",
                quant="?",
                css="a.audio",
                attr="onclick",
                callback=parse_audio_links,
            ),
            String(
                name="usage_frequency",
                quant="?",
                css="span.tag_c",
                attr="class",
                callback=parse_usage_frequency,
            ),
            Group(
                name="examples",
                css=".example_lines > .example",
                quant="*",
                children=[
                    String(name="src", css=".tag_s", quant=1, callback=normalize),
                    String(name="dst", css=".tag_t", quant=1, callback=normalize),
                ],
            ),
        ],
    ),
]

source_url_schema = [
    String(
        name="src_url",
        css="div.source_url > a",
        attr="href",
        quant="?",
    ),
    String(
        name="src_url_text",
        css="div.source_url",
        quant="?",
    ),
]


def normalize_source_url(content):
    if content["src_url"]:
        return content["src_url"]
    if content["src_url_text"]:
        return f"http://{content['src_url_text']}"
    return None


search_result_schema = Group(
    quant=1,
    children=[
        String(name="src_lang", css="div#data", attr="data-lang1", quant=1),
        String(name="dst_lang", css="div#data", attr="data-lang2", quant=1),
        String(name="query", css="div#data", attr="data-query", quant=1),
        String(
            name="correct_query",
            css="div#data",
            attr="data-correctspellingofquery",
            quant=1,
        ),
        Group(
            quant="*",
            css="div.exact > div.lemma",
            name="lemmas",
            children=lemma_schema,
        ),
        Group(
            quant="*",
            css="div.example_lines div.lemma",
            name="examples",
            children=lemma_schema,
        ),
        Group(
            quant="*",
            css="table.result_table > tbody > tr",
            name="external_sources",
            children=[
                String(
                    name="src",
                    css="td.left > div.wrap",
                    quant=1,
                    attr="_all_text",
                    callback=normalize_example,
                ),
                String(
                    name="dst",
                    css="td.right2 > div.wrap",
                    quant=1,
                    attr="_all_text",
                    callback=normalize_example,
                ),
                Group(
                    name="src_url",
                    quant=1,
                    css="td.left",
                    children=source_url_schema,
                    callback=normalize_source_url,
                ),
                Group(
                    name="dst_url",
                    quant=1,
                    css="td.right2",
                    children=source_url_schema,
                    callback=normalize_source_url,
                ),
            ],
        ),
    ],
)


autocompletions_schema = Group(
    quant=1,
    children=[
        Group(
            quant="*",
            css="div.autocompletion_item",
            name="autocompletions",
            children=[
                String(
                    name="text",
                    css="div.main_row > div.main_item",
                    quant=1,
                    callback=normalize,
                ),
                concat_values(
                    "pos",
                    String(
                        name="pos",
                        css="div.main_row > div.main_wordtype",
                        quant="*",
                    ),
                ),
                Group(
                    quant="+",
                    name="translations",
                    css="div.translation_row > div > div.translation_item",
                    children=[
                        String(
                            name="text", xpath="self::*", quant=1, callback=normalize
                        ),
                        concat_values(
                            "pos",
                            String(
                                name="pos",
                                css="div.translation_item > div.wordtype",
                                quant="*",
                            ),
                        ),
                    ],
                ),
            ],
        )
    ],
)
