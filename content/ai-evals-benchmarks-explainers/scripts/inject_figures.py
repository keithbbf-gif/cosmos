#!/usr/bin/env python3
"""Insert <figure> blocks with SEO alt text after the first two H2 headings."""

from __future__ import annotations

import re
from pathlib import Path

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- graphics-pack:v1 -->"
H2 = re.compile(r"^(## .+)$", re.M)
FM = re.compile(r"^(---\n.*?\n---\n)", re.S)


def seo_alt(art: dict, which: str) -> str:
    title = art["title"]
    if which == "timeline":
        return (
            f"Timeline of public milestones for {title}: dated anchors from the "
            f"published record, not a live leaderboard."
        )
    return (
        f"Instrument chart for {title}: how items flow to a published metric "
        f"(illustrative scoring shape, not scraped scores)."
    )


def fig_block(art: dict, which: str, n: int) -> str:
    slug = art["slug"]
    fname = "historical-timeline.svg" if which == "timeline" else "instrument-chart.svg"
    rel = f"../assets/{slug}/{fname}"
    alt = seo_alt(art, which)
    cap = (
        f"Figure {n}. Dated public anchors for this piece. Years follow the essay; "
        f"verify against BIBLIOGRAPHY.md before print."
        if which == "timeline"
        else f"Figure {n}. Scoring shape for this instrument — protocol, not a weekly rank."
    )
    return (
        f"{MARKER}\n\n"
        f'<figure class="eval-figure">\n'
        f'<img src="{rel}" alt="{alt}" width="760" height="460" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def strip_old_graphics(body: str) -> str:
    body = re.sub(r"<!-- graphics-pack:v1 -->[\s\S]*?(?=\n## |\Z)", "", body)
    body = re.sub(r"!\[[^\]]*\]\(\.\./assets/[^)]+\)\s*\n\*Figure \d+[^*]*\*\s*\n", "", body)
    return body


def inject(path: Path, art: dict) -> str:
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        raise SystemExit(f"no front matter: {path}")
    fm = m.group(1)
    body = strip_old_graphics(text[len(fm) :])
    h2s = list(H2.finditer(body))
    if len(h2s) < 2:
        return text
    inserts = [
        (h2s[0].end(), fig_block(art, "timeline", 1)),
        (h2s[1].end(), fig_block(art, "instrument", 2)),
    ]
    # apply from the end so offsets stay valid
    for pos, block in reversed(inserts):
        body = body[:pos] + "\n\n" + block + body[pos:]
    # front matter figures list
    fig_yaml = (
        "figures:\n"
        f"  - ../assets/{art['slug']}/historical-timeline.svg\n"
        f"  - ../assets/{art['slug']}/instrument-chart.svg\n"
    )
    if "figures:" not in fm:
        inner = fm[4:-4].rstrip() + "\n" + fig_yaml.rstrip() + "\n"
        fm = "---\n" + inner + "---\n"
    else:
        # repair prior bad merge (nonefigures:)
        fm = fm.replace("nonefigures:", "none\nfigures:")
    return fm + body


def main() -> None:
    by_file = {a["file"]: a for a in ARTICLES}
    for rel, art in sorted(by_file.items()):
        path = ROOT / rel
        path.write_text(inject(path, art), encoding="utf-8")
    print(f"updated figures in {len(by_file)} articles")


if __name__ == "__main__":
    main()
