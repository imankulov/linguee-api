import re
from typing import Any, Dict, List, Optional

from xextract import Group
from xextract.parsers import BaseNamedParser


def concat_values(name: str, *children: BaseNamedParser):
    """
    Concatenate values from children.

    Extract values from all the children, flatten and concatenate them as one string.
    """
    return Group(
        name=name,
        children=children,
        quant="?",
        callback=_concat_values_callback,
    )


def _concat_values_callback(objects: Dict[str, Any]) -> str:
    ret = []
    for value in objects.values():
        if isinstance(value, list):
            ret.append(" ".join(str(item) for item in value))
        else:
            ret.append(str(value))
    return normalize(" ".join(ret))


def normalize(text: str) -> str:
    """
    Replace all whitespaces in the text with a single space.

    For example "  foo   bar " is converted to "foo bar".
    """
    return re.sub(r"\s+", " ", text).strip()


def remove_round_brackets_and_split_by_commas(text: Optional[str]) -> List[str]:
    """Remove round brackets and split by commas."""
    if not text:
        return []

    stripped_text = text.strip().strip("()")
    if not stripped_text:
        return []

    return [item.strip() for item in stripped_text.split(",") if item.strip()]


def take_first_item(variants) -> Optional[str]:
    """Take the first item variant and normalize."""
    if not variants["item"]:
        return None
    return variants["item"][0]
