"""Data classes that define the schema of the API response."""
from typing import Optional, Union

from pydantic import BaseModel, Field


class AudioLink(BaseModel):
    """The link to the audio file along with the language variant."""

    url: str = Field(
        example=(
            "https://www.linguee.com/mp3/PT_BR/f5/"
            "f5491d72610965dd0a287c1ab1025c0f-300.mp3"
        )
    )
    lang: str = Field(example="Brazilian Portuguese")


class SearchResult(BaseModel):
    """The root structure of parsed API response."""

    class Lemma(BaseModel):
        """Information about one found word (lemma)."""

        class Translation(BaseModel):
            """One of the possible translation of the term."""

            featured: bool = Field(example=False)
            text: str = Field(example="required")
            pos: Optional[str] = Field(example="adjective / past participle, masculine")
            audio_links: Optional[list[AudioLink]]

        featured: bool = Field(example=False)
        text: str = Field(example="obrigado")
        pos: Optional[str] = Field(example="interjection")
        grammar_info: Optional[str] = Field(example="Akk")
        audio_links: Optional[list[AudioLink]]
        translations: list[Translation]

    class Example(BaseModel):
        """One example."""

        class Translation(BaseModel):
            """Translation example."""

            text: str = Field(example="big thanks")
            pos: Optional[str] = Field(example="n [colloq.]")

        text: str = Field(example="muito obrigado")
        pos: Optional[str] = Field(example="m")
        audio_links: Optional[list[AudioLink]]
        translations: list[Translation]

    class ExternalSource(BaseModel):
        """An example of usage of the word in the context."""

        src: str = Field(
            example=(
                "Parabéns e um grande obrigado a todos que ajudaram [...] "
                "ao sucesso desta noite!"
            )
        )
        dst: str = Field(
            example=(
                "Well done and many thanks to everyone who helped [...] "
                "make this evening a success!"
            )
        )
        src_url: str = Field(
            example="http://www.findmadeleine.com/pt/updates@page=2.html"
        )
        dst_url: str = Field(example="http://www.findmadeleine.com/updates@page=2.html")

    src_lang: str = Field(example="pt")
    dst_lang: str = Field(example="en")
    query: str = Field(example="obrigado")
    correct_query: str = Field(example="obrigado")
    lemmas: list[Lemma]
    examples: list[Example]
    external_sources: list[ExternalSource]


class Autocompletions(BaseModel):
    """The root structure of the API response for auto-completions."""

    class AutocompletionItem(BaseModel):
        """Information about one word."""

        class TranslationItem(BaseModel):
            text: str = Field(example="cat")
            pos: Optional[str] = Field(example="n")

        text: str = Field(example="Katze")
        pos: Optional[str] = Field(example="f")
        translations: list[TranslationItem]

    autocompletions: list[AutocompletionItem]


class Correction(BaseModel):
    """
    A redirect to the correct form.

    This response is returned by a parser, when a spelling issue is found, and
    a redirect to the correct form is needed.
    """

    correction: str


class NotFound(BaseModel):
    """
    LemmaTranslation not found.

    The query is not recognized as a meaningful word. Nothing to translate.
    """

    pass


class ParseError(BaseModel):
    """Unexpected parsing error. Don't know what to do."""

    message: str


SearchResultOrError = Union[SearchResult, ParseError, Correction, NotFound]
AutocompletionsOrError = Union[Autocompletions, ParseError]
