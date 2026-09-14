#!/usr/bin/env python3
"""Image + SEO pass: code-lineage SVG timelines, Commons portraits (RIGHTS.md), figure embeds.

Patches stage-*/*.md under this pack. Never AI-generated faces.
Regenerate: python3 content/counseling-ethics-history/graphics_pass.py
"""
from __future__ import annotations

import re
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path

from image_seo_specs import PORTRAIT_SPECS, TIMELINE_SPECS

ROOT = Path(__file__).resolve().parent
PLATES = ROOT / "plates"
ERA_ASSETS = ROOT / "assets" / "era"
SHARED = ROOT / "assets" / "_shared"
EMBEDS = ROOT / "embeds"

SERIES_LABEL = "WOW THERAPIES · COUNSELING ETHICS HISTORY"
ACCENT = "#2D4A6B"
UA = "WOWTherapies-Counseling-Ethics-History/1.0 (educational)"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<!-- figure-id:.*?-->\n<figure class=\"wow-figure.*?</figure>\n",
    re.S,
)

# Wikimedia Commons — verify file page on upload day
CLEARED: dict[str, dict[str, str]] = {
    "1947-tolman-committee": {
        "commons_title": "File:EDWARD CHACE TOLMAN (1886 - 1959).jpg",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "author": "See Commons file page",
        "source_url": "https://commons.wikimedia.org/wiki/File:EDWARD_CHACE_TOLMAN_(1886_-_1959).jpg",
        "download": (
            "https://upload.wikimedia.org/wikipedia/commons/5/5d/"
            "EDWARD_CHACE_TOLMAN_%281886_-_1959%29.jpg"
        ),
        "filename": "portrait.jpg",
    },
}


def parse_front(text: str) -> tuple[dict[str, str], str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}, text, ""
    block = m.group(1)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data, text[m.end() :], block


def era_timeline_svg(
    slug: str,
    title: str,
    events: list[tuple[str, str]],
    caption: str,
    highlight: int,
) -> str:
    n = len(events)
    w, h = 900, 400
    x0, x1 = 80, w - 80
    step = (x1 - x0) / max(n - 1, 1)
    ticks = []
    for i, (year, label) in enumerate(events):
        x = x0 + i * step
        hi = i == highlight
        stroke_w = 2.2 if hi else 0.8
        tick = (
            f'  <line class="tick" x1="{x:.0f}" y1="200" x2="{x:.0f}" y2="215" '
            f'stroke-width="{stroke_w}"/>'
        )
        if hi:
            tick += (
                f'\n  <circle cx="{x:.0f}" cy="210" r="7" fill="none" '
                f'stroke="{ACCENT}" stroke-width="2"/>'
            )
        year_weight = ' font-weight="bold"' if hi else ' font-weight="bold"'
        year_fill = ACCENT if hi else "#1C1A17"
        ticks.append(
            f"{tick}\n"
            f'  <text x="{x:.0f}" y="190" text-anchor="middle" class="ink" '
            f'font-size="13"{year_weight} fill="{year_fill}">{year}</text>\n'
            f'  <text x="{x:.0f}" y="240" text-anchor="middle" class="muted" '
            f'font-size="11">{label}</text>'
        )
    tick_block = "\n".join(ticks)
    cap = textwrap.shorten(caption, width=120, placeholder="…")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title} — code lineage timeline</title>
  <desc id="d">{cap}</desc>
  <defs>
    <style>
      .paper {{ fill: #F7F2E8; }}
      .ink {{ fill: #1C1A17; font-family: Georgia, 'Palatino Linotype', serif; }}
      .muted {{ fill: #5C564C; font-family: Georgia, serif; }}
      .caps {{ font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; }}
      .rule {{ stroke: #1C1A17; stroke-width: 1; fill: none; }}
      .tick {{ stroke: #1C1A17; }}
    </style>
  </defs>
  <rect class="paper" width="{w}" height="{h}"/>
  <rect x="0" y="0" width="{w}" height="6" fill="{ACCENT}"/>
  <text x="48" y="44" class="ink caps">{SERIES_LABEL}</text>
  <text x="48" y="74" class="ink" font-size="22" font-weight="bold">{title}</text>
  <line class="rule" x1="{x0:.0f}" y1="210" x2="{x1:.0f}" y2="210"/>
{tick_block}
  <rect x="40" y="300" width="820" height="80" fill="#FFF" stroke="#1C1A17" stroke-width="0.6" opacity="0.92"/>
  <text x="52" y="322" class="muted caps">Figure SEO caption</text>
  <text x="52" y="344" class="ink" font-size="12">{cap}</text>
  <text x="52" y="366" class="muted" font-size="11">Original SVG code-lineage timeline (CC0). Slug: {slug}.</text>
</svg>
"""


def type_plate_svg(name: str, dates: str, epithet: str) -> str:
    lines = textwrap.wrap(epithet, width=42)[:4]
    y0 = 300 - 12 * len(lines)
    text_lines = "\n".join(
        f'  <text x="180" y="{y0 + i * 22}" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="13" fill="#5C564C">{line}</text>'
        for i, line in enumerate(lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="440" viewBox="0 0 360 440" role="img" aria-labelledby="title desc">
  <title id="title">{name} — typographic plate</title>
  <desc id="desc">No photograph; editorial type plate for educational ethics history.</desc>
  <rect width="360" height="440" fill="#F7F2E8"/>
  <rect x="0" y="0" width="360" height="8" fill="{ACCENT}"/>
  <text x="180" y="120" text-anchor="middle" font-family="Georgia, 'Palatino Linotype', serif" font-size="11" letter-spacing="0.14em" fill="{ACCENT}">{SERIES_LABEL}</text>
  <text x="180" y="200" text-anchor="middle" font-family="Georgia, serif" font-size="22" font-weight="bold" fill="#1C1A17">{name}</text>
  <text x="180" y="232" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#5C564C">{dates}</text>
{text_lines}
  <text x="180" y="400" text-anchor="middle" font-family="Georgia, serif" font-size="10" fill="#8a8278">Typographic plate · CC0 · no AI face</text>
</svg>
"""


def timeline_figure_html(slug: str, title: str, caption: str) -> str:
    alt = f"Code ethics lineage timeline: {title}."
    return f"""
<!-- figure-id: {slug}.lead-timeline -->
<figure class="wow-figure wow-figure--era wow-figure--code-lineage">
  <img
    src="../../assets/era/{slug}/lead-timeline.svg"
    alt="{alt}"
    width="900"
    height="400"
    loading="lazy"
  />
  <figcaption>
    <strong>{title}</strong> — {caption}
    <span class="figure-credit">Original editorial code-lineage timeline (CC0). No AI-generated faces.</span>
  </figcaption>
</figure>
"""


def portrait_figure_html(slug: str, name: str, dates: str, seo: str, cleared: bool) -> str:
    plate_slug = slug
    if cleared:
        alt = f"Historical photograph of {name} ({dates}), Wikimedia Commons."
        src = f"../../plates/{plate_slug}/portrait.jpg"
        credit = (
            f'Wikimedia Commons ({CLEARED[slug]["license"]}). '
            f'See <code>plates/{plate_slug}/RIGHTS.md</code>.'
        )
        extra = ""
    else:
        alt = f"Typographic history plate for {name} ({dates}) — no photograph."
        src = f"../../plates/{plate_slug}/plate.svg"
        credit = f'Original editorial plate (CC0). See <code>plates/{plate_slug}/RIGHTS.md</code>.'
        extra = "\n    <em>Typographic plate — no likeness embedded.</em>"
    return f"""
<!-- figure-id: {slug}.lead-portrait -->
<figure class="wow-figure wow-figure--portrait">
  <img
    src="{src}"
    alt="{alt}"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>{name}</strong> ({dates}) — {seo}{extra}
    <span class="figure-credit">{credit}</span>
  </figcaption>
</figure>
"""


def write_plate_rights_typographic(path: Path, slug: str, name: str, dates: str) -> None:
    path.write_text(
        f"""# Rights — `{slug}` plate

| Field | Value |
|-------|-------|
| figure | {name} |
| life_dates | {dates} |
| status | typographic |
| file | plate.svg |
| ai_generated | no |
| ingested | 2026-09-14 |
| license | CC0 (editorial typographic plate) |
| source | Original SVG generated in-repo |
| source_url | — |
| credit_line | Typographic plate — no likeness embedded. See PORTRAIT_SOURCES.md. |

## SEO caption (`<figcaption>`)

**{name}** ({dates}) — see article `meta_description` and portrait figure block.
""",
        encoding="utf-8",
    )


def write_plate_rights_commons(path: Path, slug: str, name: str, dates: str) -> None:
    meta = CLEARED[slug]
    path.write_text(
        f"""# Rights — `{slug}` portrait

| Field | Value |
|-------|-------|
| figure | {name} |
| life_dates | {dates} |
| status | cleared |
| file | {meta['filename']} |
| ai_generated | no |
| ingested | 2026-09-14 |
| license | {meta['license']} |
| license_url | {meta['license_url']} |
| commons_title | {meta['commons_title']} |
| source_url | {meta['source_url']} |
| author | {meta['author']} |
| credit_line | {name} — Wikimedia Commons, {meta['license']}. Re-verify file page on upload day. |

## SEO caption (`<figcaption>`)

**{name}** ({dates}) — historical photograph for the Tolman committee essay; not a generated face.
""",
        encoding="utf-8",
    )


def download_commons(slug: str, dest: Path) -> None:
    meta = CLEARED[slug]
    url = meta["download"]
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dest.write_bytes(urllib.request.urlopen(req, timeout=90).read())


def write_pack_rights() -> None:
    lines = [
        "# Rights manifest — counseling ethics-code history (WOW Therapies)",
        "",
        "Pack date: 14 September 2026. Authority for every binary likeness and editorial graphic.",
        "",
        "## Policy",
        "",
        "- **Never** AI-generated or synthetic historical faces.",
        "- Raster portraits **only** when listed below with a live Wikimedia Commons file page and per-plate `RIGHTS.md`.",
        "- `assets/era/*/lead-timeline.svg` — original code-lineage timelines (CC0).",
        "- `plates/*/plate.svg` — typographic plates when no cleared Commons portrait ships (CC0).",
        "- Default for living people and unverified photos: **type only** (`PORTRAIT_SOURCES.md`).",
        "",
        "## Cleared Commons portraits",
        "",
        "| slug | file | license | commons |",
        "| --- | --- | --- | --- |",
    ]
    for slug, meta in sorted(CLEARED.items()):
        lines.append(
            f"| `{slug}` | `plates/{slug}/{meta['filename']}` | {meta['license']} | "
            f"{meta['source_url']} |"
        )
    lines.extend(
        [
            "",
            "## Editorial SVG (CC0)",
            "",
            "| kind | path pattern |",
            "| --- | --- |",
            "| Code-lineage timeline | `assets/era/<slug>/lead-timeline.svg` |",
            "| Typographic plate | `plates/<slug>/plate.svg` |",
            "",
            "Full register: `GRAPHICS_INDEX.md`. Portrait policy: `PORTRAIT_SOURCES.md`.",
            "",
        ]
    )
    (ROOT / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index() -> None:
    rows = []
    for slug in sorted(TIMELINE_SPECS):
        rows.append(
            f"| `{slug}` | `assets/era/{slug}/lead-timeline.svg` | ready | CC0 editorial |"
        )
    port_rows = []
    for slug in sorted(PORTRAIT_SPECS):
        st = "commons" if slug in CLEARED else "typographic"
        port_rows.append(f"| `{slug}` | `plates/{slug}/` | {st} | see plate RIGHTS |")
    text = f"""# GRAPHICS_INDEX — counseling-ethics-history

Canonical register for lead graphics. Regenerate: `python3 graphics_pass.py`

## Code-lineage timelines ({len(TIMELINE_SPECS)})

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows)}

## Portrait plates ({len(PORTRAIT_SPECS)})

| Slug | Folder | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(port_rows)}

## Embed templates

- `embeds/code-lineage-figure-block.md`
- `embeds/portrait-figure-block.md`

## Status legend

- **ready** — CC0 editorial SVG embedded in draft.
- **commons** — Wikimedia Commons raster + `RIGHTS.md`.
- **typographic** — No likeness; name/dates plate only.
"""
    (ROOT / "GRAPHICS_INDEX.md").write_text(text, encoding="utf-8")


def write_embed_templates() -> None:
    EMBEDS.mkdir(parents=True, exist_ok=True)
    (EMBEDS / "code-lineage-figure-block.md").write_text(
        """<!-- figure-id: {slug}.lead-timeline -->
<figure class="wow-figure wow-figure--era wow-figure--code-lineage">
  <img src="../../assets/era/{slug}/lead-timeline.svg" alt="{alt}" width="900" height="400" loading="lazy" />
  <figcaption><strong>{title}</strong> — {caption}
  <span class="figure-credit">Original editorial code-lineage timeline (CC0).</span></figcaption>
</figure>
""",
        encoding="utf-8",
    )
    (EMBEDS / "portrait-figure-block.md").write_text(
        """<!-- figure-id: {slug}.lead-portrait -->
<figure class="wow-figure wow-figure--portrait">
  <img src="../../plates/{slug}/portrait.jpg" alt="{alt}" width="360" height="440" loading="lazy" />
  <figcaption><strong>{name}</strong> ({dates}) — {seo}
  <span class="figure-credit">Wikimedia Commons — see plates/{slug}/RIGHTS.md</span></figcaption>
</figure>
""",
        encoding="utf-8",
    )


def build_assets() -> None:
    SHARED.mkdir(parents=True, exist_ok=True)
    PLATES.mkdir(parents=True, exist_ok=True)
    ERA_ASSETS.mkdir(parents=True, exist_ok=True)

    for slug, (title, events, caption, highlight) in TIMELINE_SPECS.items():
        folder = ERA_ASSETS / slug
        folder.mkdir(parents=True, exist_ok=True)
        svg = era_timeline_svg(slug, title, events, caption, highlight)
        (folder / "lead-timeline.svg").write_text(svg, encoding="utf-8")

    for slug, (name, dates, seo) in PORTRAIT_SPECS.items():
        folder = PLATES / slug
        folder.mkdir(parents=True, exist_ok=True)
        if slug in CLEARED:
            dest = folder / CLEARED[slug]["filename"]
            if not dest.is_file():
                download_commons(slug, dest)
            write_plate_rights_commons(folder / "RIGHTS.md", slug, name, dates)
        else:
            (folder / "plate.svg").write_text(type_plate_svg(name, dates, seo), encoding="utf-8")
            write_plate_rights_typographic(folder / "RIGHTS.md", slug, name, dates)


def upsert_front(front: str, key: str, value: str) -> str:
    pat = rf"^{key}:.*$"
    if re.search(pat, front, flags=re.M):
        return re.sub(pat, f'{key}: {value}', front, count=1, flags=re.M)
    return front + f"\n{key}: {value}"


def patch_drafts() -> None:
    needle = "not a substitute for care with a licensed clinician."
    paths = sorted(ROOT.glob("stage-*/*.md"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        fm, body, front = parse_front(text)
        slug = fm.get("slug", "")
        if slug not in TIMELINE_SPECS:
            print(f"WARN {path.name}: missing timeline spec for {slug}")
            continue
        body = FIGURE_RE.sub("\n", body)
        idx = body.find(needle)
        if idx == -1:
            print(f"WARN {path.name}: no disclaimer needle")
            continue
        insert_at = idx + len(needle)

        title, _ev, caption, _hi = TIMELINE_SPECS[slug]
        figs = timeline_figure_html(slug, title, caption)
        lead = f"assets/era/{slug}/lead-timeline.svg"
        front = upsert_front(front, "lead_asset", f'"{lead}"')
        front = upsert_front(front, "portrait_status", "essay-only")

        if slug in PORTRAIT_SPECS:
            name, dates, seo = PORTRAIT_SPECS[slug]
            cleared = slug in CLEARED
            figs += portrait_figure_html(slug, name, dates, seo, cleared)
            if cleared:
                portrait_path = f"plates/{slug}/{CLEARED[slug]['filename']}"
                front = upsert_front(front, "portrait", f'"{portrait_path}"')
                front = upsert_front(front, "figure_dates", f'"{dates}"')
                front = upsert_front(front, "portrait_status", "commons-cleared")
            else:
                front = upsert_front(front, "portrait", f'"plates/{slug}/plate.svg"')
                front = upsert_front(front, "portrait_status", "typographic")

        body = body[:insert_at] + "\n" + figs + body[insert_at:]
        path.write_text(f"---\n{front}\n---\n{body}", encoding="utf-8")
        print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    if len(TIMELINE_SPECS) != 48:
        raise SystemExit(f"expected 48 timeline specs, got {len(TIMELINE_SPECS)}")
    write_embed_templates()
    build_assets()
    write_pack_rights()
    write_graphics_index()
    patch_drafts()
    print("done")


if __name__ == "__main__":
    main()
