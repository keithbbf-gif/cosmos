# -*- coding: utf-8 -*-
"""Collect figure / media paths from frontmatter and markdown for WXR media notes."""
from __future__ import annotations

import json
import re
from typing import Any

_IMAGE_MD_RE = re.compile(
    r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)"
)


def _norm_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def figures_from_frontmatter(meta: dict[str, Any]) -> list[str]:
    out: list[str] = []
    figs = meta.get("figures")
    if figs is None:
        return out
    if isinstance(figs, str):
        out.append(_norm_path(figs))
        return out
    if isinstance(figs, list):
        for item in figs:
            if isinstance(item, str):
                out.append(_norm_path(item))
            elif isinstance(item, dict):
                for k in ("path", "src", "file", "href"):
                    if k in item and item[k]:
                        out.append(_norm_path(str(item[k])))
                        break
    return out


def figures_from_markdown(body_md: str) -> list[str]:
    return [_norm_path(m.group(1)) for m in _IMAGE_MD_RE.finditer(body_md)]


def collect_figure_paths(meta: dict[str, Any], body_md: str) -> list[str]:
    """Unique ordered list of media paths referenced by the post."""
    seen: set[str] = set()
    ordered: list[str] = []
    for p in figures_from_frontmatter(meta) + figures_from_markdown(body_md):
        if not p or p.startswith("http://") or p.startswith("https://"):
            continue
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    return ordered


def media_notes_json(paths: list[str]) -> str:
    return json.dumps(paths, ensure_ascii=False)


def media_notes_html_comment(paths: list[str]) -> str:
    if not paths:
        return ""
    lines = ["<!-- cosmos-media-notes"]
    for p in paths:
        lines.append(f"  figure: {p}")
    lines.append("-->")
    return "\n".join(lines)
