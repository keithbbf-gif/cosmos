#!/usr/bin/env python3
"""Insert SEO <figure> blocks: timeline, concept chart, and one archival plate."""

from __future__ import annotations

import re
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from pack_data import ARTICLES

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "figures" / "REGISTRY.toml"
MARKER = "<!-- graphics-pack:nlp-bt-v1 -->"
FM = re.compile(r"^(---\n.*?\n---\n)", re.S)


def load_plates() -> dict:
    data = tomllib.loads(REGISTRY.read_text(encoding="utf-8"))
    return data.get("plates", data)


def seo_alt(art: dict, which: str) -> str:
    title = art["title"]
    if which == "timeline":
        return (
            f"Timeline of public milestones for {title}: dated anchors from the "
            f"published record, not scraped leaderboard data."
        )
    if which == "concept":
        return (
            f"Concept chart for {title}: schematic of the method or task shape "
            f"(illustrative, not a copyrighted paper figure)."
        )
    return f"Archival reference plate for {title}."


def fig_block(art: dict, which: str, n: int) -> str:
    slug = art["slug"]
    if which == "timeline":
        fname = "historical-timeline.svg"
        cap = (
            f"Figure {n}. Dated public anchors for this piece. Years follow the essay; "
            f"verify against the prose before print."
        )
        cls = "nlp-bt-figure"
    elif which == "concept":
        fname = "concept-chart.svg"
        cap = f"Figure {n}. Schematic of the method or task — editorial diagram, not live scores."
        cls = "nlp-bt-figure"
    else:
        raise ValueError(which)
    rel = f"../assets/{slug}/{fname}"
    alt = seo_alt(art, which)
    return (
        f"{MARKER}\n\n"
        f'<figure class="{cls}">\n'
        f'<img src="{rel}" alt="{alt}" width="760" height="460" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def archival_fig(art: dict, plates: dict, n: int) -> str:
    key = art["plate"]
    plate = plates.get(key)
    if not plate:
        raise KeyError(f"missing plate {key} for {art['slug']}")
    src = plate["src"]
    alt = plate.get("alt", seo_alt(art, "archival"))
    credit = plate.get("credit", "See RIGHTS.md.")
    license_line = plate.get("license", "Rights documented in RIGHTS.md.")
    w = plate.get("width", 760)
    h = plate.get("height")
    size = f'width="{w}"'
    if h:
        size += f' height="{h}"'
    return (
        f"{MARKER}\n\n"
        f'<figure class="nlp-bt-figure nlp-bt-figure--archival">\n'
        f'<img src="{src}" alt="{alt}" {size} loading="lazy" decoding="async" />\n'
        f"<figcaption>Figure {n}. {credit} License: {license_line}</figcaption>\n"
        f"</figure>\n"
    )


def strip_old(body: str) -> str:
    body = re.sub(r"<!-- graphics-pack:nlp-bt-v1 -->\s*\n", "", body)
    body = re.sub(r'<figure class="nlp-bt-figure[\s\S]*?</figure>\s*\n', "", body)
    return body


def first_para_end(body: str) -> int | None:
    body = body.lstrip("\n")
    m = re.match(r"^# .+\n\n", body)
    if not m:
        return None
    rest = body[m.end() :]
    end = rest.find("\n\n")
    if end < 0:
        return len(body)
    return m.end() + end


def patch_frontmatter(fm: str, art: dict) -> str:
    inner = fm[4:-4]
    lines = inner.splitlines()
    keys = {ln.split(":", 1)[0].strip() for ln in lines if ":" in ln and not ln.strip().startswith("-")}

    def set_kv(k: str, v: str) -> None:
        nonlocal lines, keys
        if k in keys:
            lines = [ln for ln in lines if not ln.startswith(f"{k}:")]
        lines.append(f"{k}: {v}")
        keys.add(k)

    cleaned: list[str] = []
    skipping = False
    for ln in lines:
        if ln.startswith("figures:"):
            skipping = True
            continue
        if skipping:
            if ln.startswith("  - ") or ln.startswith("- "):
                continue
            skipping = False
        cleaned.append(ln)
    lines = cleaned

    set_kv("portrait", "null")
    set_kv("portrait_status", "essay-only")
    set_kv("image_rights", "documented")
    set_kv("image_pass", "2026-09-14")
    set_kv("figure_id", art["plate"])
    meta = art["meta_description"].replace('"', '\\"')
    set_kv("meta_description", f'"{meta}"')
    fig_lines = [
        "figures:",
        f"  - ../assets/{art['slug']}/historical-timeline.svg",
        f"  - ../assets/{art['slug']}/concept-chart.svg",
        f"  - {art['plate']}",
    ]
    lines.extend(fig_lines)
    return "---\n" + "\n".join(lines) + "\n---\n"


def inject(path: Path, art: dict, plates: dict) -> None:
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        raise SystemExit(f"no front matter: {path}")
    fm = patch_frontmatter(m.group(1), art)
    body = strip_old(text[len(m.group(1)) :])
    lead = body.lstrip("\n")
    offset = len(body) - len(lead)
    pos = first_para_end(lead)
    if pos is None:
        raise SystemExit(f"could not find lead paragraph: {path}")
    block = (
        "\n\n"
        + fig_block(art, "timeline", 1)
        + "\n"
        + fig_block(art, "concept", 2)
        + "\n"
        + archival_fig(art, plates, 3)
    )
    insert_at = offset + pos
    body = body[:insert_at] + block + body[insert_at:]
    path.write_text(fm + body, encoding="utf-8")


def main() -> None:
    plates = load_plates()
    for art in ARTICLES:
        inject(ROOT / art["file"], art, plates)
    print(f"injected figures in {len(ARTICLES)} essays")


if __name__ == "__main__":
    main()
