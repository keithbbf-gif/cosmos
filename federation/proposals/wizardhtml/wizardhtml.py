"""Static day-one wizard.

The page is three files and no build step. A peer install cannot spend the
clock on a frontend toolchain. The model key is not part of this text; the
person pastes it later, and the page is not a place to keep it.
"""

from __future__ import annotations

from pathlib import Path

from cosmos_federation import ROUTE_SETUP, Refuse, secret_shape

SCHEMA = "cosmos-federation-wizardhtml/1"

_PAGE_NAME = "wizard.html"


def page_text() -> str:
    """Return wizard.html from this proposal directory.

    Refuse a document that drifted off the two day-one doors, picked up a
    secret-shaped sample, or lost the setup route. Those are page bugs, not
    something the browser should paper over.
    """
    text = (Path(__file__).resolve().parent / _PAGE_NAME).read_text(encoding="utf-8")
    lowered = text.lower()
    if "anthropic" in lowered or "claude" in lowered:
        raise Refuse("ANTHROPIC_OFF", "off the page")
    if 'value="openrouter"' not in text or 'value="xai"' not in text:
        raise Refuse("DOOR", "day-one doors missing")
    if secret_shape(text):
        raise Refuse("SECRET", "page text")
    if ROUTE_SETUP not in text:
        raise Refuse("PAGE", "setup route missing")
    return text


__all__ = ["SCHEMA", "page_text"]
