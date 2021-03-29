"""Data classed that define the schema of the API response."""
from typing import Optional

from pydantic import BaseModel, Field


class WordProperties(BaseModel):
    pos: str = Field(example="noun")
    gender: Optional[str] = Field(example="feminine")


class LemmaForm(BaseModel):
    """Variant of the lemma (how it would be in plural, feminine, etc)."""

    text: str = Field(example="obrigada")
    form_type: WordProperties = Field()


class AudioLink(BaseModel):
    """The link to the audio file along with the language variant."""

    url_part: str = Field(example="PT_BR/f5/f5491d72610965dd0a287c1ab1025c0f-300")
    lang: str = Field(example="Brazilian Portuguese")


class TranslationExample(BaseModel):
    source: str = Field(
        example="Estou obrigado pelo contrato a trabalhar seis horas por dia."
    )
    target: str = Field(example="I am bound by the contract to work six hours a day.")


class Translation(BaseModel):
    """One of the possible translation of the term."""

    featured: str = Field(example=False)
    text: str = Field(example="required")
    bid: str = Field(example="10003211476")
    lemma_id: str = Field(example="EN:required5162")
    word_type: WordProperties = Field()
    audio_links: list[AudioLink]
    examples: list[TranslationExample]


class Lemma(BaseModel):
    """Information about one found word (lemma)."""

    featured: bool = Field(example=False)
    wt: bool = Field(example=1000)
    lemma_id: str = Field(example="PT:obrigado49462")
    text: str = Field(example="obrigado")
    word_type: WordProperties
    audio_links: list[AudioLink]
    forms: list[LemmaForm]
    translations: list[Translation]


class RealExample(BaseModel):
    """An example of usage of the word in the context."""

    id: str = Field(example="row_0_8255523216_0")
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
    url: str = Field(example="http://www.findmadeleine.com/pt/updates@page=2.html")


class APIResponse(BaseModel):
    """The root structure of parsed API response."""

    src_lang: str = Field(example="pt")
    dst_lang: str = Field(example="en")
    query: str = Field(example="obrigado")
    correct_query: str = Field(example="obrigado")
    exact_matches: list[Lemma]
    inexact_matches: list[Lemma]
    real_examples: list[RealExample]
