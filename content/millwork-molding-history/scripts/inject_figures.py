#!/usr/bin/env python3
"""Replace markdown image blocks with SEO <figure> elements."""

from __future__ import annotations

import re
from pathlib import Path

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "articles"
MARKER = "<!-- graphics-pack:v1 -->"
H2 = re.compile(r"^(## .+)$", re.M)


def seo_alt(art: dict, which: str) -> str:
    title = art["title"]
    if which == "timeline":
        return (
            f"Historical timeline for {title}: dated millwork and pattern-book "
            f"anchors (verify years in prose before print)."
        )
    return (
        f"Shop plate for {title}: illustrative moulding sections on shop paper, "
        f"not a knife-grind template."
    )


def fig_block(art: dict, which: str, n: int) -> str:
    slug = art["slug"]
    fname = "historical-timeline.svg" if which == "timeline" else "shop-plate.svg"
    rel = f"../assets/{slug}/{fname}"
    alt = seo_alt(art, which)
    h2 = art["h2"]
    cap = (
        f"Figure {n}. {art['anchors'][0][1]} through {art['anchors'][-1][1]} — "
        f"see “{h2[0]}.”"
        if which == "timeline"
        else f"Figure {n}. Profile plate for “{h2[1]}.” Line sections, not a grind."
    )
    return (
        f"{MARKER}\n\n"
        f'<figure class="millwork-figure">\n'
        f'<img src="{rel}" alt="{alt}" width="760" height="460" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def historical_fig(art: dict, n: int) -> str | None:
    hist = ROOT / "assets" / art["slug"] / "historical-plate.jpg"
    if not hist.exists():
        return None
    rel = f"../assets/{art['slug']}/historical-plate.jpg"
    meta_path = ROOT / "assets" / art["slug"] / "historical-plate.json"
    credit = "Public-domain or CC-licensed scan; see RIGHTS.md."
    if meta_path.exists():
        import json

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        credit = meta.get("caption", credit)
        alt = meta.get(
            "alt",
            f"Historical millwork plate for {art['title']} from {meta.get('source', 'public archive')}.",
        )
    else:
        alt = f"Historical millwork reference plate for {art['title']}."
    return (
        f"{MARKER}\n\n"
        f'<figure class="millwork-figure millwork-figure--historical">\n'
        f'<img src="{rel}" alt="{alt}" width="760" loading="lazy" decoding="async" />\n'
        f"<figcaption>Figure {n}. {credit}</figcaption>\n"
        f"</figure>\n"
    )


def strip_old(body: str) -> str:
    body = re.sub(r"<!-- graphics-pack:v1 -->\s*\n", "", body)
    body = re.sub(
        r"<figure class=\"millwork-figure[\s\S]*?</figure>\s*\n",
        "",
        body,
    )
    body = re.sub(
        r"!\[[^\]]*\]\(\.\./assets/[^)]+\)\s*\n\*Figure \d+[^*]*\*\s*\n",
        "",
        body,
    )
    return body


def inject_article(path: Path, art: dict) -> None:
    text = path.read_text(encoding="utf-8")
    # split YAML front matter (may include multiline lists)
    if not text.startswith("---\n"):
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        return
    fm = text[: end + 5]
    body = strip_old(text[end + 5 :])
    h2s = list(H2.finditer(body))
    if len(h2s) < 2:
        return
    block1 = fig_block(art, "timeline", 1)
    block2 = fig_block(art, "shop", 2)
    hist = historical_fig(art, 3)
    body = body[: h2s[0].end()] + "\n\n" + block1 + body[h2s[0].end() :]
    h2s = list(H2.finditer(body))
    insert_at = h2s[1].end()
    if hist:
        body = body[:insert_at] + "\n\n" + block2 + "\n\n" + hist + body[insert_at:]
    else:
        body = body[:insert_at] + "\n\n" + block2 + body[insert_at:]
    path.write_text(fm + body, encoding="utf-8")


def main() -> None:
    for art in ARTICLES:
        path = ART_DIR / art["file"]
        if path.exists():
            inject_article(path, art)
    print(f"injected figures for {len(ARTICLES)} articles")


if __name__ == "__main__":
    main()
