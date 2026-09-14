#!/usr/bin/env python3
"""Image + SEO pass: era SVG timelines, PD period-object facsimiles (Pratt/Moreno), typographic plates.

PD/CC raster portraits only when listed in CLEARED (empty — see PORTRAIT_SOURCES.md).
Never AI-generated faces. Patches content/group-therapy-history/articles/*.md.
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "articles"
PLATES = ROOT / "plates"
ERA_ASSETS = ROOT / "assets" / "era"
SHARED = ROOT / "assets" / "_shared"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<!-- figure-id:.*?-->\n<figure class=\"wow-figure.*?</figure>\n",
    re.S,
)

SERIES_LABEL = "WOW THERAPIES · GROUP THERAPY HISTORY"
PACK_NAME = "group-therapy-history"

FIGURE_DATES: dict[str, str] = {}

ERA_SPECS: dict[str, tuple[str, list[tuple[str, str]], str]] = {
    "before-the-circle": (
        "Before the circle was a clinic",
        [
            ("antiquity", "Congregations & drill"),
            ("1889", "Hull-House opens"),
            ("1905", "Pratt's TB class"),
            ("1935", "Akron fellowship"),
        ],
        "Circles of prayer, ward, settlement, and mutual aid before the group hour was billed.",
    ),
    "pratt-classes-boston": (
        "Pratt's classes and the Boston origin story",
        [
            ("1900", "Osler: treat at home"),
            ("1905", "Emmanuel Church class"),
            ("1907", "JAMA class method"),
            ("1940s", "Guild elects Pratt"),
        ],
        "Massachusetts General and Emmanuel Church: medical regimen plus a weekly class.",
    ),
    "interwar-hospital-groups": (
        "Interwar hospital groups",
        [
            ("1920s", "Ward lectures"),
            ("1930s", "Schilder at Bellevue"),
            ("1938", "Psychotherapy groups"),
            ("1940s", "War psychiatry"),
        ],
        "Full wards, revival meetings, and the first hospital group write-ups.",
    ),
    "psychodrama-rooms": (
        "Psychodrama rooms",
        [
            ("1921", "Theatre of Spontaneity"),
            ("1934", "Who Shall Survive?"),
            ("1940s", "Beacon, New York"),
            ("1970s", "Quarrel with Slavson"),
        ],
        "Moreno's stage, audience, and the 1934 book that named sociometry.",
    ),
    "group-analysis-northfield": (
        "Group analysis after Northfield",
        [
            ("1942", "Hollymoor experiment"),
            ("1943", "Foulkes arrives"),
            ("1946", "Lancet papers"),
            ("1952", "Group Analytic Society"),
        ],
        "Northfield, Hollymoor, and Foulkes's group-analytic line — not Bion's.",
    ),
    "bion-tavistock": (
        "Basic assumptions: Bion and Tavistock",
        [
            ("1943", "Lancet Northfield"),
            ("1950s", "Tavistock training"),
            ("1961", "Experiences in Groups"),
            ("1970s", "Basic assumptions taught"),
        ],
        "Wilfred Bion's dependency, fight-flight, and pairing as historical theory.",
    ),
    "t-groups-ntl": (
        "T-groups and Bethel",
        [
            ("1946", "New Britain workshop"),
            ("1947", "Bethel laboratory"),
            ("1960s", "NTL trainings"),
            ("1970s", "Corporate exports"),
        ],
        "Lewin's field theory and the here-and-now training group at Bethel.",
    ),
    "encounter-boom": (
        "Encounter, Esalen, and First Facts",
        [
            ("1960s", "Esalen weekends"),
            ("1970", "Yalom group text"),
            ("1973", "First Facts study"),
            ("1980s", "Retreat fatigue"),
        ],
        "Encounter weekends and the 1973 study that counted casualties.",
    ),
    "aa-mutual-aid": (
        "AA and the fellowship that refused to be therapy",
        [
            ("1935", "Akron meetings"),
            ("1939", "Big Book"),
            ("1950s", "Traditions fixed"),
            ("1970s", "Clinicians borrow language"),
        ],
        "Mutual aid that refused the name therapy — history, not a meeting manual.",
    ),
    "therapeutic-community-cmhc": (
        "Therapeutic community and CMHC",
        [
            ("1953", "Jones Therapeutic Community"),
            ("1957", "Main at Cassel"),
            ("1963", "U.S. CMHC Act"),
            ("1970s", "Day hospitals"),
        ],
        "Jones, Main, and community mental health after the asylum.",
    ),
    "feminist-consciousness-raising": (
        "Consciousness-raising and the political circle",
        [
            ("1967", "Chicago WLM"),
            ("1968", "Redstockings"),
            ("1970s", "CR spreads"),
            ("1980s", "Therapy borrows language"),
        ],
        "Political circles that were not billed as psychotherapy.",
    ),
    "child-activity-groups": (
        "Children's activity groups",
        [
            ("1943", "Slavson introduction"),
            ("1950s", "Jewish Board shops"),
            ("1960s", "Activity vs talk"),
            ("1970s", "Training films"),
        ],
        "Slavson's activity groups: children in a shop, not a talk hour.",
    ),
    "structured-cbt-groups": (
        "When the manual entered the circle",
        [
            ("1970", "Yalom craft book"),
            ("1979", "Beck depression manual"),
            ("1987", "Group cognitive texts"),
            ("1990s", "Managed-care arithmetic"),
        ],
        "Manuals and psychoeducation inside the circle from the 1970s–1990s.",
    ),
    "agpa-profession": (
        "AGPA and group as a profession",
        [
            ("1943", "Hotel New Yorker"),
            ("1952", "AGPA renamed"),
            ("1960s", "Training standards"),
            ("1980s", "Section quarrels"),
        ],
        "A luncheon that became a guild — profession and quarrel, not a pitch.",
    ),
    "group-research-factors": (
        "Factors, cohesion, and outcome arguments",
        [
            ("1961", "Frank Persuasion and Healing"),
            ("1970", "Yalom factors"),
            ("1973", "First Facts"),
            ("1990s", "Burlingame reviews"),
        ],
        "How group research learned to count cohesion and outcomes.",
    ),
    "telehealth-groups-history": (
        "Groups on a wire",
        [
            ("1990s", "Telephone groups"),
            ("2000s", "Forums & lists"),
            ("2010s", "Video pilots"),
            ("2020", "Pandemic shift"),
        ],
        "Therapy groups on telephone, forum, and video — history, not a how-to.",
    ),
}

PERIOD_OBJECTS: dict[str, dict[str, str]] = {
    "pratt-classes-boston": {
        "work_title": "The Class Method of Treating Consumption in the Homes of the Poor",
        "author": "Joseph H. Pratt, M.D.",
        "imprint": "Journal of the American Medical Association, vol. 49, no. 9",
        "year": "1907",
        "license": "Public domain (U.S. publication 1907)",
        "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
        "source_note": "Typographic facsimile for staging — replace with verified *JAMA* scan on upload day.",
    },
    "psychodrama-rooms": {
        "work_title": "Who Shall Survive?",
        "author": "Jacob L. Moreno, M.D.",
        "imprint": "Beacon House · Beacon, N.Y.",
        "year": "1934",
        "license": "Staging facsimile — verify U.S. status before live publish",
        "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
        "source_note": "Typographic facsimile for staging — replace with library scan of the 1934 title page on upload day.",
    },
}

CLEARED: dict[str, dict] = {}


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


def figure_dates_from_meta(meta: str) -> str:
    if re.search(r"\bliving\b", meta, re.I):
        return "living (verified 2026)"
    m = re.search(r"\((\d{4}\s*[–—-]\s*[^)]+)\)", meta)
    if m:
        return m.group(1).strip()
    m = re.search(r"\(b\.\s*(\d{4})\)", meta, re.I)
    if m:
        return f"b. {m.group(1)}"
    return "dates unverified"


def load_figure_specs() -> dict[str, tuple[str, str, str]]:
    specs: dict[str, tuple[str, str, str]] = {}
    for path in sorted(ART.glob("*.md")):
        fm, _, _ = parse_front(path.read_text(encoding="utf-8"))
        if fm.get("type") != "figure":
            continue
        slug = fm.get("slug", "")
        if not slug:
            continue
        name = fm.get("title", slug.replace("-", " ").title())
        meta = fm.get("meta_description", "")
        dates = FIGURE_DATES.get(slug) or figure_dates_from_meta(meta)
        seo = meta
        if len(seo) > 220:
            seo = textwrap.shorten(seo, width=220, placeholder="…")
        specs[slug] = (name, dates, seo)
    return specs


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
  <desc id="desc">No photograph; editorial type plate for educational history.</desc>
  <rect width="360" height="440" fill="#F7F2E8"/>
  <rect x="0" y="0" width="360" height="8" fill="#6B2D3E"/>
  <text x="180" y="120" text-anchor="middle" font-family="Georgia, 'Palatino Linotype', serif" font-size="10" letter-spacing="0.12em" fill="#6B2D3E">{SERIES_LABEL}</text>
  <text x="180" y="200" text-anchor="middle" font-family="Georgia, serif" font-size="22" font-weight="bold" fill="#1C1A17">{name}</text>
  <text x="180" y="232" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#5C564C">{dates}</text>
{text_lines}
  <text x="180" y="400" text-anchor="middle" font-family="Georgia, serif" font-size="10" fill="#8a8278">Typographic plate · CC0 · no AI face</text>
</svg>
"""


def era_timeline_svg(slug: str, title: str, events: list[tuple[str, str]], caption: str) -> str:
    n = len(events)
    w, h = 900, 400
    x0, x1 = 80, w - 80
    step = (x1 - x0) / max(n - 1, 1)
    ticks = []
    for i, (year, label) in enumerate(events):
        x = x0 + i * step
        ticks.append(
            f'  <line class="tick" x1="{x:.0f}" y1="200" x2="{x:.0f}" y2="215"/>'
            f'\n  <text x="{x:.0f}" y="190" text-anchor="middle" class="ink" font-size="13" font-weight="bold">{year}</text>'
            f'\n  <text x="{x:.0f}" y="240" text-anchor="middle" class="muted" font-size="11">{label}</text>'
        )
    tick_block = "\n".join(ticks)
    cap = textwrap.shorten(caption, width=120, placeholder="…")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title} — editorial timeline</title>
  <desc id="d">{cap}</desc>
  <defs>
    <style>
      .paper {{ fill: #F7F2E8; }}
      .ink {{ fill: #1C1A17; font-family: Georgia, 'Palatino Linotype', serif; }}
      .muted {{ fill: #5C564C; font-family: Georgia, serif; }}
      .caps {{ font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; }}
      .rule {{ stroke: #1C1A17; stroke-width: 1; fill: none; }}
      .tick {{ stroke: #1C1A17; stroke-width: 0.8; }}
    </style>
  </defs>
  <rect class="paper" width="{w}" height="{h}"/>
  <rect x="0" y="0" width="{w}" height="6" fill="#6B2D3E"/>
  <text x="48" y="44" class="ink caps">Group therapy history</text>
  <text x="48" y="74" class="ink" font-size="22" font-weight="bold">{title}</text>
  <line class="rule" x1="{x0}" y1="210" x2="{x1}" y2="210"/>
{tick_block}
  <rect x="40" y="300" width="820" height="80" fill="#FFF" stroke="#1C1A17" stroke-width="0.6" opacity="0.92"/>
  <text x="52" y="322" class="muted caps">Caption</text>
  <text x="52" y="344" class="ink" font-size="12">{caption}</text>
  <text x="52" y="366" class="muted" font-size="11">Original SVG timeline (CC0). Slug: {slug}.</text>
</svg>
"""


def period_object_svg(slug: str, meta: dict[str, str]) -> str:
    w, h = 900, 400
    title = meta["work_title"]
    author = meta["author"]
    imprint = meta["imprint"]
    year = meta["year"]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">Title page facsimile — {title}</title>
  <desc id="d">Typographic staging facsimile of a public-domain title page. Not a photograph. No faces.</desc>
  <rect fill="#F7F2E8" width="{w}" height="{h}"/>
  <rect x="0" y="0" width="{w}" height="6" fill="#6B2D3E"/>
  <text x="450" y="48" text-anchor="middle" font-family="Georgia, serif" font-size="11" letter-spacing="0.14em" fill="#6B2D3E">PERIOD OBJECT · PD TITLE PAGE (FACSIMILE)</text>
  <rect x="120" y="80" width="660" height="260" fill="#FFF" stroke="#1C1A17" stroke-width="1"/>
  <text x="450" y="150" text-anchor="middle" font-family="Georgia, serif" font-size="28" font-weight="bold" fill="#1C1A17">{title}</text>
  <text x="450" y="190" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#5C564C">{author}</text>
  <text x="450" y="230" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#5C564C">{imprint}</text>
  <text x="450" y="270" text-anchor="middle" font-family="Georgia, serif" font-size="20" fill="#1C1A17">{year}</text>
  <text x="52" y="360" font-family="Georgia, serif" font-size="11" fill="#5C564C">{meta['license']} — {meta['source_note']}</text>
  <text x="52" y="380" font-family="Georgia, serif" font-size="11" fill="#5C564C">Slug: {slug}. Replace with verified library/GPO scan before live publish.</text>
</svg>
"""


def write_plate_rights(path: Path, slug: str, name: str, dates: str, status: str) -> None:
    path.write_text(
        f"""# Rights — `{slug}` plate

| Field | Value |
|-------|-------|
| figure | {name} |
| life_dates | {dates} |
| status | {status} |
| file | plate.svg |
| ai_generated | no |
| ingested | 2026-09-14 |
| license | CC0 (editorial typographic plate) |
| source | Original SVG generated in-repo |
| source_url | — |
| credit_line | Typographic plate — no likeness embedded. See PORTRAIT_SOURCES.md. |

## SEO caption (`<figcaption>`)

**{name}** ({dates}) — see article `meta_description` and figure block.
""",
        encoding="utf-8",
    )


def write_period_rights(path: Path, slug: str, meta: dict[str, str]) -> None:
    path.write_text(
        f"""# Rights — `{slug}` period object

| Field | Value |
|-------|-------|
| work | {meta['work_title']} |
| author | {meta['author']} |
| year | {meta['year']} |
| status | pd-facsimile |
| file | lead-period-object.svg |
| ai_generated | no |
| ingested | 2026-09-14 |
| license | {meta['license']} |
| license_url | {meta['license_url']} |
| source | Typographic facsimile for staging — human uploads verified scan on publish day |
| credit_line | Image: title page of {meta['work_title']}, {meta['author']}, {meta['year']}. License: {meta['license']}. |

See `PORTRAIT_SOURCES.md` for upload-day re-verification.
""",
        encoding="utf-8",
    )


def figure_html(slug: str, name: str, dates: str, seo: str) -> str:
    alt = f"Typographic history plate for {name} ({dates}) — no photograph."
    return f"""
<!-- figure-id: {slug}.lead-plate -->
<figure class="wow-figure wow-figure--portrait wow-figure--portrait-typographic">
  <img
    src="../plates/{slug}/plate.svg"
    alt="{alt}"
    width="360"
    height="440"
    loading="lazy"
  />
  <figcaption>
    <strong>{name}</strong> ({dates}) — {seo}
    <em>Typographic plate — no likeness embedded.</em>
    <span class="figure-credit">Original editorial plate (CC0). See <code>plates/{slug}/RIGHTS.md</code>.</span>
  </figcaption>
</figure>
"""


def era_timeline_html(slug: str, title: str, caption: str) -> str:
    alt = f"Editorial timeline for {title}."
    return f"""
<!-- figure-id: {slug}.lead-timeline -->
<figure class="wow-figure wow-figure--era">
  <img
    src="../assets/era/{slug}/lead-timeline.svg"
    alt="{alt}"
    width="900"
    height="400"
    loading="lazy"
  />
  <figcaption>
    <strong>{title}</strong> — {caption}
    <span class="figure-credit">Original editorial timeline (CC0). No AI-generated faces.</span>
  </figcaption>
</figure>
"""


def era_period_html(slug: str, meta: dict[str, str], caption: str) -> str:
    alt = (
        f"Typographic facsimile of the title page of {meta['work_title']}, "
        f"{meta['author']}, {meta['year']} — public domain, no photograph."
    )
    return f"""
<!-- figure-id: {slug}.lead-period-object -->
<figure class="wow-figure wow-figure--era wow-figure--period-object">
  <img
    src="../assets/era/{slug}/lead-period-object.svg"
    alt="{alt}"
    width="900"
    height="400"
    loading="lazy"
  />
  <figcaption>
    <strong>{meta['work_title']}</strong> ({meta['year']}) — {caption}
    <span class="figure-credit">PD period object (facsimile for staging). {meta['license']}. See <code>assets/era/{slug}/RIGHTS.md</code>.</span>
  </figcaption>
</figure>
"""


def write_pack_rights() -> None:
    lines = [
        "# Rights manifest — group therapy history (WOW Therapies)",
        "",
        "Pack date: 14 September 2026. Authority for every binary likeness and editorial graphic.",
        "",
        "## Policy",
        "",
        "- **Never** AI-generated or synthetic historical faces.",
        "- Raster portraits only when cleared below (PD/CC with a live file-page license).",
        "- Typographic `plates/*/plate.svg` and `assets/era/*/lead-timeline.svg` are original editorial art (CC0).",
        "- PD/staging title-page facsimiles: `assets/era/pratt-classes-boston/` (Pratt 1907 *JAMA*) and "
        "`assets/era/psychodrama-rooms/` (Moreno 1934) — replace with verified scans on upload day.",
        "- Per-plate detail: `plates/<slug>/RIGHTS.md`. Era graphics: `GRAPHICS_INDEX.md`.",
        "",
        "## Cleared raster portraits",
        "",
    ]
    if not CLEARED:
        lines.append(
            "_None shipped in this pass — typographic plates only; see `PORTRAIT_SOURCES.md`._"
        )
    lines.extend(
        [
            "",
            "## PD period objects (facsimile SVG for staging)",
            "",
            "| slug | work | license |",
            "| --- | --- | --- |",
            "| `pratt-classes-boston` | Pratt, class method in *JAMA* (1907) | PD (U.S. 1907) |",
            "| `psychodrama-rooms` | Moreno, *Who Shall Survive?* (1934) | Staging facsimile — verify on upload |",
            "",
            "## Editorial SVG (CC0)",
            "",
            "| kind | path pattern |",
            "| --- | --- |",
            "| Era timeline | `assets/era/<slug>/lead-timeline.svg` |",
            "| Era PD object | `assets/era/<slug>/lead-period-object.svg` |",
            "| Figure type plate | `plates/<slug>/plate.svg` |",
            "",
        ]
    )
    (ROOT / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index(figure_specs: dict[str, tuple[str, str, str]]) -> None:
    rows_era = []
    for slug in sorted(ERA_SPECS):
        if slug in PERIOD_OBJECTS:
            rows_era.append(
                f"| `{slug}` | `assets/era/{slug}/lead-period-object.svg` | pd-facsimile | PD + staging RIGHTS |"
            )
        else:
            rows_era.append(
                f"| `{slug}` | `assets/era/{slug}/lead-timeline.svg` | ready | CC0 editorial |"
            )
    rows_fig = []
    for slug in sorted(figure_specs):
        st = "cleared" if slug in CLEARED else "typographic"
        rows_fig.append(f"| `{slug}` | `plates/{slug}/plate.svg` | {st} | CC0 or see plate RIGHTS |")
    text = f"""# GRAPHICS_INDEX — {PACK_NAME}

Canonical register for lead graphics. Regenerate: `python3 graphics_pass.py`

## Era leads (16)

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows_era)}

## Figure plates (28)

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows_fig)}

## Embed templates

- `embeds/era-figure-block.md`
- `embeds/figure-plate-block.md`

## Status legend

- **ready** — CC0 editorial SVG timeline embedded in article.
- **pd-facsimile** — Pratt 1907 *JAMA* or Moreno 1934 title-page facsimile per `PORTRAIT_SOURCES.md`.
- **typographic** — No PD/CC likeness; name/dates plate only.
- **cleared** — PD/CC raster (none in default pass).
"""
    (ROOT / "GRAPHICS_INDEX.md").write_text(text, encoding="utf-8")


def build_assets(figure_specs: dict[str, tuple[str, str, str]]) -> None:
    SHARED.mkdir(parents=True, exist_ok=True)
    PLATES.mkdir(parents=True, exist_ok=True)
    ERA_ASSETS.mkdir(parents=True, exist_ok=True)

    for slug, (title, events, caption) in ERA_SPECS.items():
        folder = ERA_ASSETS / slug
        folder.mkdir(parents=True, exist_ok=True)
        if slug in PERIOD_OBJECTS:
            meta = PERIOD_OBJECTS[slug]
            (folder / "lead-period-object.svg").write_text(
                period_object_svg(slug, meta), encoding="utf-8"
            )
            write_period_rights(folder / "RIGHTS.md", slug, meta)
            # Timeline still generated for optional inline use / WP featured alternates
            (folder / "lead-timeline.svg").write_text(
                era_timeline_svg(slug, title, events, caption), encoding="utf-8"
            )
        else:
            (folder / "lead-timeline.svg").write_text(
                era_timeline_svg(slug, title, events, caption), encoding="utf-8"
            )

    for slug, (name, dates, seo) in figure_specs.items():
        folder = PLATES / slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "plate.svg").write_text(type_plate_svg(name, dates, seo), encoding="utf-8")
        write_plate_rights(folder / "RIGHTS.md", slug, name, dates, "typographic")


def patch_articles(figure_specs: dict[str, tuple[str, str, str]]) -> None:
    needle = "not a substitute for care with a licensed clinician."
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body, front = parse_front(text)
        slug = fm.get("slug", "")
        if not slug:
            continue
        body = FIGURE_RE.sub("\n", body)
        idx = body.find(needle)
        if idx == -1:
            print(f"WARN {path.name}: no disclaimer needle")
            continue
        insert_at = idx + len(needle)

        if fm.get("type") == "era" and slug in ERA_SPECS:
            title, _ev, caption = ERA_SPECS[slug]
            if slug in PERIOD_OBJECTS:
                fig = era_period_html(slug, PERIOD_OBJECTS[slug], caption)
                lead = f"assets/era/{slug}/lead-period-object.svg"
            else:
                fig = era_timeline_html(slug, title, caption)
                lead = f"assets/era/{slug}/lead-timeline.svg"
            if "lead_asset:" not in front:
                front += f'\nlead_asset: "{lead}"'
            else:
                front = re.sub(r'^lead_asset:.*$', f'lead_asset: "{lead}"', front, count=1, flags=re.M)
            if "portrait_status:" not in front:
                front += "\nportrait_status: essay-only"
            else:
                front = re.sub(
                    r"^portrait_status:.*$", "portrait_status: essay-only", front, count=1, flags=re.M
                )
            body = body[:insert_at] + "\n" + fig + body[insert_at:]
        elif fm.get("type") == "figure" and slug in figure_specs:
            name, dates, seo = figure_specs[slug]
            fig = figure_html(slug, name, dates, seo)
            portrait_path = f"plates/{slug}/plate.svg"
            front = re.sub(r"^portrait:.*$", f'portrait: "{portrait_path}"', front, count=1, flags=re.M)
            if "figure_dates:" not in front:
                front += f'\nfigure_dates: "{dates}"'
            if "portrait_status:" not in front:
                front += "\nportrait_status: typographic"
            else:
                front = re.sub(
                    r"^portrait_status:.*$", "portrait_status: typographic", front, count=1, flags=re.M
                )
            body = body[:insert_at] + "\n" + fig + body[insert_at:]
        else:
            print(f"skip {path.name} (unknown slug {slug})")
            continue

        path.write_text(f"---\n{front}\n---\n{body}", encoding="utf-8")
        print(f"patched {path.name}")


def main() -> None:
    figure_specs = load_figure_specs()
    if len(figure_specs) != 28:
        raise SystemExit(f"expected 28 figure specs, got {len(figure_specs)}")
    build_assets(figure_specs)
    write_pack_rights()
    write_graphics_index(figure_specs)
    patch_articles(figure_specs)
    print("done")


if __name__ == "__main__":
    main()
