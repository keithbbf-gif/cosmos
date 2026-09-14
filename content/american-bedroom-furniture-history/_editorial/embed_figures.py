#!/usr/bin/env python3
"""Insert lead museum <figure> blocks, original SVG diagrams, and SEO image frontmatter."""

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
DRAFTS = ROOT / "drafts"
WRITER_SLUGS = ROOT / "writer-slugs.json"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
FIGURE_MARK = "<!-- abfh-figure:v1 -->"
DIAGRAM_MARK = "<!-- abfh-diagram:v1 -->"
FIGURE_CLASS = "abfh-figure"
DIAGRAM_CLASS = "abfh-diagram"


def load_plates() -> dict[str, dict]:
    data = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    return dict(data.get("plates", {}))


def load_assignments() -> dict[str, tuple[str, str, str]]:
    data = tomllib.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, str, str]] = {}
    for slug, block in data.items():
        if slug == "series":
            continue
        out[slug] = (block["plate"], block["alt"], block["caption"])
    return out


def rights_line(plate: dict) -> str:
    return (
        f"{plate['license']}; {plate['institution']}; "
        f'<a href="{plate["source_page"]}">source</a>. {plate["credit"]}'
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


def diagram_html(slug: str, chapter: str, period: str) -> str:
    rel = f"../assets/diagrams/{slug}/lead-timeline.svg"
    alt = (
        f"Original timeline diagram for chapter {chapter} ({period}) on the "
        f"American bedroom furniture series axis; furniture silhouettes only."
    )
    return (
        f"{DIAGRAM_MARK}\n"
        f'<figure class="{DIAGRAM_CLASS}">\n'
        f'  <img src="{rel}" alt="{alt}" width="960" height="220" '
        f'loading="lazy" decoding="async"/>\n'
        f"  <figcaption><strong>Fig. 2.</strong> Chapter placement on the series "
        f"timeline — original SVG diagram (not a museum photograph).</figcaption>\n"
        f"</figure>\n"
    )


def patch_frontmatter(fm: str, plate_key: str, slug: str) -> str:
    """Add or update image and SEO fields without flattening multi-line YAML."""
    fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
    dek = fields.get("dek", "").strip().strip('"')
    new_kv = {
        "figure_id": f"plates.{plate_key}",
        "diagram_id": f"diagrams.{slug}.lead-timeline",
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


def replace_block(body: str, mark: str, new_block: str, figure_end: str = "</figure>\n") -> str:
    if mark in body:
        return re.sub(
            rf"{re.escape(mark)}.*?{re.escape(figure_end)}",
            new_block,
            body,
            count=1,
            flags=re.S,
        )
    return body


def embed_file(path: Path, plates: dict[str, dict], assignments: dict[str, tuple[str, str, str]]) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        print(f"skip (no frontmatter): {path}", file=sys.stderr)
        return False
    fm = m.group(1)
    body = raw[m.end() :]
    fields = dict(re.findall(r"^([a-z_]+):\s*(.+)$", fm, re.M))
    slug = fields.get("slug", "").strip().strip('"')
    if slug not in assignments:
        print(f"skip (no assignment): {slug} {path}", file=sys.stderr)
        return False
    plate_key, alt, caption = assignments[slug]
    plate = plates[plate_key]
    fig = figure_html(plate, alt, caption)
    diagram = diagram_html(
        slug,
        fields.get("chapter", "?"),
        fields.get("period", "American bedroom furniture"),
    )
    body = replace_block(body, FIGURE_MARK, fig)
    body = replace_block(body, DIAGRAM_MARK, diagram)
    if FIGURE_MARK not in body:
        lines = body.splitlines()
        out: list[str] = []
        inserted = False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("# "):
                out.append("")
                out.append(fig.rstrip())
                out.append(diagram.rstrip())
                out.append("")
                inserted = True
        body = "\n".join(out) + ("\n" if raw.endswith("\n") else "")
    elif DIAGRAM_MARK not in body:
        body = body.replace(fig, fig + diagram, 1)
    new_fm = patch_frontmatter(fm, plate_key, slug)
    path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
    return True


def main() -> int:
    plates = load_plates()
    assignments = load_assignments()
    missing_plates = {pk for pk, _, _ in assignments.values() if pk not in plates}
    if missing_plates:
        print("registry missing plates:", missing_plates, file=sys.stderr)
        return 2
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["slugs"]
    if set(slugs) != set(assignments):
        only_writer = set(slugs) - set(assignments)
        only_assign = set(assignments) - set(slugs)
        if only_writer or only_assign:
            print("slug mismatch writer vs assignments:", only_writer, only_assign, file=sys.stderr)
            return 2
    n = 0
    for slug in slugs:
        path = DRAFTS / f"{slug}.md"
        if embed_file(path, plates, assignments):
            n += 1
    print(f"embedded figures in {n} drafts")
    return 0 if n == len(slugs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
