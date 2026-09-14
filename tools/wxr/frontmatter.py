# -*- coding: utf-8 -*-
"""Parse markdown with YAML frontmatter; strip internal COSMOS fields."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n",
    re.DOTALL,
)

_STRIP_KEYS = frozenset({"voice_check"})


@dataclass
class ParsedPost:
    meta: dict[str, Any]
    body_md: str
    stripped_keys: list[str] = field(default_factory=list)


def parse_markdown(text: str) -> ParsedPost:
    """Split frontmatter and body; remove keys that must not ship to WordPress."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return ParsedPost(meta={}, body_md=text.lstrip("\ufeff"), stripped_keys=[])

    raw_meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(raw_meta, dict):
        raw_meta = {}

    stripped: list[str] = []
    meta: dict[str, Any] = {}
    for key, val in raw_meta.items():
        if key in _STRIP_KEYS:
            stripped.append(key)
            continue
        meta[key] = val

    body = text[m.end() :]
    return ParsedPost(meta=meta, body_md=body, stripped_keys=stripped)


def meta_string(meta: dict[str, Any], key: str, default: str = "") -> str:
    val = meta.get(key, default)
    if val is None:
        return default
    return str(val).strip()
