#!/usr/bin/env python3
"""Insert <figure> blocks with SEO alt text (timeline, diagram, optional product photo)."""

from __future__ import annotations

import re
from pathlib import Path

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- chip-magazine-graphics:v1 -->"
FM = re.compile(r"^(---\n.*?\n---\n)", re.S)
SOURCES = re.compile(r"^## Sources\s*$", re.M)
H1 = re.compile(r"^# .+\n\n", re.M)


def seo_alt(art: dict, which: str) -> str:
    title = art["title"]
    if which == "timeline":
        return (
            f"Timeline of public milestones for {title}: dated anchors from press releases, "
            f"papers, and product records — not live benchmark scores."
        )
    if which == "photo":
        return (
            f"Historical product photograph for {title}: licensed hardware image, "
            f"no generated faces. See RIGHTS.md for attribution."
        )
    return (
        f"Architecture diagram for {title}: illustrative GPU or datacenter shape from the "
        f"public record, not an official vendor block diagram."
    )


def fig_block(art: dict, which: str, n: int) -> str:
    slug = art["slug"]
    if which == "timeline":
        fname = "historical-timeline.svg"
        cap = (
            f"Figure {n}. Calendar anchors for this piece. Years follow the essay; "
            f"verify against Sources before publication."
        )
    elif which == "photo":
        fname = art["photo"]
        rel = f"../assets/{slug}/{fname}"
        alt = seo_alt(art, which)
        cap = (
            f"Figure {n}. Licensed product photograph (hardware only). "
            f"Attribution and license: RIGHTS.md."
        )
        return (
            f"{MARKER}\n\n"
            f'<figure class="chip-figure chip-figure-photo">\n'
            f'<img src="{rel}" alt="{alt}" width="760" height="507" loading="lazy" decoding="async" />\n'
            f"<figcaption>{cap}</figcaption>\n"
            f"</figure>\n"
        )
    else:
        fname = "architecture-diagram.svg"
        cap = (
            f"Figure {n}. Illustrative system shape for the argument — protocol and architecture, "
            f"not scraped silicon photography unless noted."
        )
    rel = f"../assets/{slug}/{fname}"
    alt = seo_alt(art, which)
    return (
        f"{MARKER}\n\n"
        f'<figure class="chip-figure">\n'
        f'<img src="{rel}" alt="{alt}" width="760" height="460" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def strip_old_graphics(body: str) -> str:
    body = re.sub(r"<!-- chip-magazine-graphics:v1 -->\s*\n", "", body)
    body = re.sub(
        r'<figure class="chip-figure[^"]*">[\s\S]*?</figure>\s*\n',
        "",
        body,
    )
    return body


def inject(path: Path, art: dict) -> str:
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        raise SystemExit(f"no front matter: {path}")
    fm = m.group(1)
    body = strip_old_graphics(text[len(fm) :]).lstrip("\n")

    h1m = H1.match(body)
    insert_timeline = 0
    if h1m:
        insert_timeline = h1m.end()
        rest = body[insert_timeline:]
        para_end = rest.find("\n\n")
        if para_end != -1:
            insert_timeline += para_end + 2

    blocks: list[tuple[int, str]] = []
    if insert_timeline:
        blocks.append((insert_timeline, fig_block(art, "timeline", 1)))

    src = SOURCES.search(body)
    diagram_n = 2
    if src:
        tail = fig_block(art, "diagram", diagram_n)
        if art.get("photo"):
            tail += fig_block(art, "photo", diagram_n + 1)
        blocks.append((src.start(), tail))

    for pos, block in sorted(blocks, key=lambda x: x[0], reverse=True):
        body = body[:pos] + "\n\n" + block + body[pos:]

    fig_lines = [
        "figures:",
        f"  - ../assets/{art['slug']}/historical-timeline.svg",
        f"  - ../assets/{art['slug']}/architecture-diagram.svg",
    ]
    if art.get("photo"):
        fig_lines.append(f"  - ../assets/{art['slug']}/{art['photo']}")
    fig_yaml = "\n".join(fig_lines) + "\n"
    if "portrait:" not in fm:
        fm = fm[:-4].rstrip() + "\nportrait: null\n" + fig_yaml + "---\n"
    elif "figures:" not in fm:
        fm = fm[:-4].rstrip() + "\n" + fig_yaml + "---\n"
    else:
        inner = fm[4:-4]
        inner = re.sub(r"figures:\n(?:  - .+\n)+", fig_yaml, inner)
        if "figures:" not in inner:
            inner = inner.rstrip() + "\n" + fig_yaml.rstrip() + "\n"
        fm = "---\n" + inner + "---\n"

    return fm + body


def main() -> None:
    by_file = {a["file"]: a for a in ARTICLES}
    for rel, art in sorted(by_file.items()):
        path = ROOT / rel
        out = inject(path, art)
        path.write_text(out, encoding="utf-8")
    print(f"injected figures into {len(by_file)} articles")


if __name__ == "__main__":
    main()
