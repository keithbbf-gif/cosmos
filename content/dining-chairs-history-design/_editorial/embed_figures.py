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
DRAFTS = ROOT / "drafts"
WRITER_SLUGS = ROOT / "writer-slugs.json"

FRONT = re.compile(r"^---\n(.*?)\n---", re.S)
FIGURE_MARK = "<!-- dchd-figure:v1 -->"
FIGURE_CLASS = "dchd-figure"
IMAGE_PASS = "2026-09-14"


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


def patch_frontmatter(fm: str, plate_key: str) -> str:
    new_kv = {
        "figure_id": f"plates.{plate_key}",
        "image_rights": "documented",
        "image_pass": IMAGE_PASS,
        "voice_check": "edited",
    }
    lines = fm.splitlines()
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if ":" in line and not line.startswith(" "):
            key = line.split(":", 1)[0].strip()
            if key in new_kv:
                out.append(f"{key}: {new_kv[key]}")
                seen.add(key)
                continue
        out.append(line)
    if seen != set(new_kv):
        insert_at = len(out)
        for i, line in enumerate(out):
            if line.startswith("optional_links:") or line.startswith("verify:") or line.startswith("figures:"):
                insert_at = i
                break
        missing = [f"{key}: {new_kv[key]}" for key in new_kv if key not in seen]
        out[insert_at:insert_at] = missing + ([""] if insert_at < len(out) else [])
    return "\n".join(out)


def embed_file(path: Path, plates: dict[str, dict], assignments: dict[str, tuple[str, str, str]]) -> bool:
    raw = path.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        print(f"skip (no frontmatter): {path}", file=sys.stderr)
        return False
    fm = m.group(1)
    body = raw[m.end() :]
    slug_m = re.search(r'^slug:\s*"?([^"\n]+)"?\s*$', fm, re.M)
    slug = slug_m.group(1).strip() if slug_m else ""
    if slug not in assignments:
        print(f"skip (no assignment): {slug} {path}", file=sys.stderr)
        return False
    plate_key, alt, caption = assignments[slug]
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
            if not inserted and line.startswith("# "):
                out.append(line)
                out.append("")
                out.append(fig.rstrip())
                out.append("")
                inserted = True
                continue
            out.append(line)
        if not inserted:
            trimmed = body.lstrip("\n")
            body = "\n" + fig.rstrip() + "\n\n" + trimmed
            if raw.endswith("\n") and not body.endswith("\n"):
                body += "\n"
        else:
            body = "\n".join(out) + ("\n" if raw.endswith("\n") else "")
    new_fm = patch_frontmatter(fm, plate_key)
    path.write_text(f"---\n{new_fm}\n---{body}", encoding="utf-8")
    return True


def main() -> int:
    plates = load_plates()
    assignments = load_assignments()
    missing_plates = {pk for pk, _, _ in assignments.values() if pk not in plates}
    if missing_plates:
        print("registry missing plates:", missing_plates, file=sys.stderr)
        return 2
    slugs = json.loads(WRITER_SLUGS.read_text(encoding="utf-8"))["reading_order"]
    slug_names = [row["slug"] for row in slugs]
    if set(slug_names) != set(assignments):
        only_writer = set(slug_names) - set(assignments)
        only_assign = set(assignments) - set(slug_names)
        if only_writer or only_assign:
            print("slug mismatch writer vs assignments:", only_writer, only_assign, file=sys.stderr)
            return 2
    n = 0
    for slug in slug_names:
        path = DRAFTS / f"{slug}.md"
        if not path.is_file():
            for p in DRAFTS.glob(f"*-{slug}.md"):
                path = p
                break
        if embed_file(path, plates, assignments):
            n += 1
    print(f"embedded figures in {n} drafts")
    return 0 if n == len(slug_names) else 1


if __name__ == "__main__":
    raise SystemExit(main())
