#!/usr/bin/env python3
"""Validate figure SEO embeds for fig-grafting-budding IMAGE pass."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "GRAPHICS_INDEX.md"
FIGURE_ROW = re.compile(
    r"^\|\s*`(?P<id>[^`]+)`\s*\|\s*`(?P<path>[^`]+)`",
    re.M,
)
FIGURE_ID_COMMENT = re.compile(r"<!--\s*figure-id:\s*(?P<id>[\w.-]+)\s*-->")
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)


def parse_index() -> dict[str, Path]:
    text = INDEX.read_text(encoding="utf-8")
    out: dict[str, Path] = {}
    for m in FIGURE_ROW.finditer(text):
        fid = m.group("id")
        rel = m.group("path")
        out[fid] = ROOT / rel
    return out


def yaml_list(meta: dict[str, str], key: str) -> list[str]:
    raw = meta.get(key, "")
    if not raw:
        return []
    return [x.strip().strip("- ").strip("'\"") for x in raw.splitlines() if x.strip()]


def parse_front(text: str) -> dict[str, str]:
    m = FRONT.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    block = m.group(1)
    key: str | None = None
    buf: list[str] = []
    for line in block.splitlines():
        if line.strip().startswith("figures:"):
            key = "figures"
            buf = []
            continue
        if key == "figures":
            if re.match(r"^\w+:", line):
                out["figures"] = "\n".join(buf)
                key = None
                if ":" in line:
                    k, v = line.split(":", 1)
                    out[k.strip()] = v.strip().strip("'\"")
            else:
                buf.append(line)
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("'\"")
    if key == "figures":
        out["figures"] = "\n".join(buf)
    return out


def main() -> int:
    if not INDEX.is_file():
        print("FAIL missing GRAPHICS_INDEX.md")
        return 1

    registered = parse_index()
    errors: list[str] = []

    for fid, path in registered.items():
        if not path.is_file():
            errors.append(f"index {fid}: missing file {path.relative_to(ROOT)}")

    drafts_with_figures: list[Path] = []
    for path in sorted(ROOT.glob("stage-*/*.md")):
        text = path.read_text(encoding="utf-8")
        meta = parse_front(text)
        figs = yaml_list(meta, "figures")
        if not figs:
            continue
        drafts_with_figures.append(path)
        if "meta_description:" not in text:
            errors.append(f"{path.name}: figures declared but missing meta_description")
        if "slug:" not in text:
            errors.append(f"{path.name}: figures declared but missing slug")
        if "<figure>" not in text:
            errors.append(f"{path.name}: missing <figure> SEO block")
        comments = [m.group("id") for m in FIGURE_ID_COMMENT.finditer(text)]
        for fid in figs:
            if fid not in registered:
                errors.append(f"{path.name}: unknown figure id {fid!r}")
            if fid not in comments:
                errors.append(f"{path.name}: missing <!-- figure-id: {fid} -->")
        for fid in comments:
            if fid not in figs:
                errors.append(f"{path.name}: comment {fid!r} not in front matter figures:")

    if not drafts_with_figures:
        errors.append("no drafts declare figures: — embed pass incomplete")

    print(f"registered_figures={len(registered)} drafts_with_figures={len(drafts_with_figures)}")
    for e in errors:
        print(f"FAIL {e}")
    if errors:
        return 1
    print("PASS figure SEO embeds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
