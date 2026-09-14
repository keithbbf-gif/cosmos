#!/usr/bin/env python3
"""Insert lead <figure> blocks and SEO image frontmatter from REGISTRY + assignments."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
ASSIGNMENTS_PATH = Path(__file__).resolve().parent / "figure_assignments.toml"
WRITER_SLUGS = ROOT / "writer-slugs.json"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
FIGURE_MARK = "<!-- lrch-figure:v1 -->"
FIGURE_CLASS = "lrch-figure"


def load_registry() -> dict[str, dict]:
    data = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    plates = dict(data.get("plates", {}))
    plates.update(data.get("schematics", {}))
    return plates


def load_assignments() -> dict[str, tuple[str, str, str]]:
    data = tomllib.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, str, str]] = {}
    for slug, block in data.items():
        if slug == "series":
            continue
        out[slug] = (block["plate"], block["alt"], block["caption"])
    return out


def rights_line(plate: dict) -> str:
    source = plate["source_page"]
    if not source.startswith("http"):
        source = f"../{source}"
    return (
        f"{plate['license']}; {plate['institution']}; "
        f'<a href="{source}">source</a>. {plate["credit"]}'
    )


def figure_html(plate: dict, alt: str, caption: str) -> str:
    w = plate.get("width", 1200)
    h = plate.get("height", 900)
    rights = rights_line(plate)
    return (
        f"{FIGURE_MARK}\n"
        f'<figure class="{FIGURE_CLASS}">\n'
        f'  <img src="{plate["src"]}" alt="{alt}" width="{w}" height="{h}" '
        f'loading="lazy" decoding="async"/>\n'
        f"  <figcaption><strong>Fig. 1.</strong> {caption} "
        f"<em>Rights:</em> {rights}</figcaption>\n"
        f"</figure>\n"
    )


def patch_frontmatter(fm: str, plate_key: str) -> str:
    fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
    dek = fields.get("dek", "").strip().strip('"')
    new_kv = {
        "figure_id": plate_key,
        "image_rights": "documented",
        "image_pass": "2026-09-14",
    }
    if dek and "meta_description" not in fields:
        new_kv["meta_description"] = dek
    lines = fm.splitlines()
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if ":" in line and not line.startswith(" "):
            key = line.split(":", 1)[0].strip()
            if key in new_kv:
                val = new_kv[key]
                if " " in val or ":" in val:
                    out.append(f'{key}: "{val}"')
                else:
                    out.append(f"{key}: {val}")
                seen.add(key)
                continue
        out.append(line)
    if seen != set(new_kv):
        if out and out[-1].strip():
            out.append("")
        for key, val in new_kv.items():
            if key not in seen:
                if " " in val or ":" in val:
                    out.append(f'{key}: "{val}"')
                else:
                    out.append(f"{key}: {val}")
    return "\n".join(out)


def embed_file(path: Path, plates: dict[str, dict], assignments: dict[str, tuple[str, str, str]]) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        print(f"skip (no frontmatter): {path}", file=sys.stderr)
        return False
    fm = m.group(1)
    body = raw[m.end() :]
    slug = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M)).get("slug", "").strip().strip('"')
    if slug not in assignments:
        print(f"skip (no assignment): {slug} {path}", file=sys.stderr)
        return False
    plate_key, alt, caption = assignments[slug]
    if plate_key not in plates:
        print(f"skip (missing plate): {plate_key}", file=sys.stderr)
        return False
    plate = plates[plate_key]
    fig = figure_html(plate, alt, caption)
    if FIGURE_MARK in body:
        body = re.sub(
            rf"{re.escape(FIGURE_MARK)}.*?</figure>\n",
            fig,
            body,
            count=1,
            flags=re.S,
        )
    else:
        lines = body.splitlines()
        out: list[str] = []
        inserted = False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("# "):
                out.append("")
                out.append(fig.rstrip())
                out.append("")
                inserted = True
        body = "\n".join(out) + ("\n" if raw.endswith("\n") else "")
    new_fm = patch_frontmatter(fm, plate_key)
    path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
    return True


def main() -> int:
    plates = load_registry()
    assignments = load_assignments()
    missing = {pk for pk, _, _ in assignments.values() if pk not in plates}
    if missing:
        print("registry missing keys:", missing, file=sys.stderr)
        return 2
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["slugs"]
    if set(slugs) != set(assignments):
        only_writer = set(slugs) - set(assignments)
        only_assign = set(assignments) - set(slugs)
        print("slug mismatch:", only_writer, only_assign, file=sys.stderr)
        return 2
    n = 0
    for slug in slugs:
        path = ROOT / f"{slug}.md"
        if embed_file(path, plates, assignments):
            n += 1
    print(f"embedded figures in {n} object drafts")
    return 0 if n == len(slugs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
