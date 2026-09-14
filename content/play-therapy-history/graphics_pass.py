#!/usr/bin/env python3
"""Image + SEO pass: era SVG timelines, typographic figure plates, RIGHTS.md, <figure> embeds.

PD/CC raster portraits only when listed in CLEARED (empty by default for this pack).
Never AI-generated faces.
"""
from __future__ import annotations

import re
import textwrap
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
PLATES = ROOT / "plates"
ERA_ASSETS = ROOT / "assets" / "era"
SHARED = ROOT / "assets" / "_shared"
UA = "WOWTherapies-Play-Therapy-History/1.0 (educational; keith.bbf@gmail.com)"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<!-- figure-id:.*?-->\n<figure class=\"wow-figure.*?</figure>\n",
    re.S,
)

FIGURE_SPECS: dict[str, tuple[str, str, str]] = {'ann-jernberg-theraplay': ('Ann M. Jernberg',
                            '1927–1993',
                            'clinical social worker who published Theraplay in 1979 as structured attachment play.'),
 'anna-freud-play-technique': ('Anna Freud',
                               '1895–1982',
                               'child analyst who treated play as useful and insufficient in her 1927 technique book.'),
 'charles-schaefer-prescriptive': ('Charles E. Schaefer',
                                   '1933–2020',
                                   'APT co-founder who edited prescriptive play-therapy handbooks for decades.'),
 'clark-moustakas': ('Clark Moustakas',
                     '1923–2012',
                     'psychologist who wrote early play-therapy texts and later humanistic theory.'),
 'david-levy-release-therapy': ('David M. Levy',
                                '1893–1977',
                                'psychiatrist who named release therapy in a 1938 paper on play and discharge.'),
 'dora-kalff-sandplay': ('Dora M. Kalff',
                         '1904–1990',
                         'Jungian analyst who named sandplay and trained a tray-based school.'),
 'eliana-gil-trauma-lane': ('Eliana Gil',
                            '1948–',
                            'trauma clinician whose 1991 Healing Power of Play named a family-therapy lane.'),
 'erikson-toys-and-reasons': ('Erik H. Erikson',
                              '1902–1994',
                              'psychoanalyst who read toys and play configurations as developmental evidence.'),
 'garry-landreth-unt': ('Garry L. Landreth',
                        '1937–2026',
                        'UNT professor who built a child-centered play-therapy training center in Denton.'),
 'guerney-filial-1964': ('Bernard & Louise Guerney',
                         '1923–2019',
                         'filial-therapy authors whose 1964 paper named parents as therapeutic agents.'),
 'hermine-hug-hellmuth': ('Hermine Hug-Hellmuth',
                          '1871–1924',
                          'Vienna analyst whose 1921 IJP paper named child-analysis technique before Klein or Axline.'),
 'john-allan-jungian': ('John A. B. Allan',
                        '1935–',
                        'Jungian counselor whose 1988 Inscapes put archetypal play on the training shelf.'),
 'kevin-oconnor-ecosystemic': ("Kevin J. O'Connor",
                               '1952–',
                               'APT co-founder who later named ecosystemic play therapy.'),
 'margaret-lowenfeld': ('Margaret Lowenfeld',
                        '1890–1973',
                        'founder of the World Technique and the Institute of Child Psychology in London.'),
 'melanie-klein-play-technique': ('Melanie Klein',
                                  '1882–1960',
                                  "analyst whose 1932 book treated play as the child's free association."),
 'terry-kottman-adlerian': ('Terry Kottman',
                            '1941–',
                            'counselor educator who named Adlerian play therapy in Partners in Play (1995).'),
 'violet-oaklander': ('Violet Oaklander',
                      '1927–2021',
                      'Gestalt child therapist whose 1978 Windows to Our Children named a school.'),
 'virginia-axline-1947': ('Virginia M. Axline',
                          '1911–1988',
                          "counselor who published Play Therapy in 1947 with Rogers's non-directive manners."),
 'winnicott-playing-and-reality': ('D. W. Winnicott',
                                   '1896–1971',
                                   'pediatrician-analyst whose 1971 Playing and Reality made play a theory of '
                                   'culture.')}

ERA_SPECS: dict[str, tuple[str, list[tuple[str, str]], str]] = {'apt-1982': ('Association for Play Therapy, 1982',
              [('1982', 'APT incorporated'),
               ('1990s', 'RPT credential'),
               ('2000s', 'State lobbying'),
               ('2010s', 'School presence')],
              "Schaefer and O'Connor's 1982 society as an association object, not a room photo."),
 'bapt-and-uk-registration': ('BAPT and UK registration',
                              [('1992', 'BAPT founded'),
                               ('2000s', 'HCPC debates'),
                               ('2010s', 'Title protection'),
                               ('2020s', 'Training routes')],
                              'British registration quarrels beside an American credential boom.'),
 'bratton-2005-meta': ('Bratton et al., 2005',
                       [('1990s', 'Outcome trials'),
                        ('2005', 'Meta-analysis'),
                        ('2010s', 'Effect-size fights'),
                        ('2020s', 'Manual pressure')],
                       'A 2005 meta-analysis that gave the field a graph and not a resting place.'),
 'child-centered-after-axline': ('Child-centered after Axline',
                                 [('1947', 'Play Therapy book'),
                                  ('1970s', 'CCPT naming'),
                                  ('1982', 'APT forms'),
                                  ('2000s', 'School CCPT trials')],
                                 'How child-centered play therapy became a school name, film library, and credential '
                                 'path.'),
 'controversial-discussions-play': ('Controversial Discussions',
                                    [('1941', 'London meetings begin'),
                                     ('1943', 'Klein vs Anna Freud'),
                                     ('1944', 'Middle group'),
                                     ('1946', 'Society splits')],
                                    "British Psychoanalytical Society fights about transference in the child's play."),
 'dibs-1964': ('Dibs in Search of Self',
               [('1947', 'Axline method book'),
                ('1964', 'Dibs published'),
                ('1970s', 'Film adaptations'),
                ('2000s', 'Ethics reread')],
               'How a 1964 case narrative made one child a public object without becoming clip art.'),
 'evidence-fights': ('Evidence fights',
                     [('1990s', 'EST language'),
                      ('2005', 'Bratton meta'),
                      ('2010s', 'Manual wars'),
                      ('2020s', 'Process vs protocol')],
                     'After 2005 the field carried a graph and still wanted a handout.'),
 'gender-of-the-profession': ('Gender of the profession',
                              [('1940s', 'Women guidance workers'),
                               ('1970s', 'Feminist therapy'),
                               ('1982', 'APT leadership'),
                               ('2000s', 'Majority-women workforce')],
                              'A majority-women field with a mixed-gender origin story and credential politics.'),
 'hospital-play-emma-plank': ('Hospital play',
                              [('1950s', 'Postwar pediatrics'),
                               ('1962', 'Plank hospital book'),
                               ('1970s', 'Child-life staff'),
                               ('1990s', 'Evidence language')],
                              'Emma Plank named play as hospital work before outpatient play therapy owned the word.'),
 'international-journal-1992': ('International Journal, 1992',
                                [('1992', 'IJPT volume 1'),
                                 ('1990s', 'Peer review norms'),
                                 ('2005', 'Meta-analysis era'),
                                 ('2010s', 'Open access fights')],
                                "APT's journal as a bound object that made play therapy look like a literature."),
 'play-is-older-than-a-clinic': ('Play is older than a clinic',
                                 [('1800s', 'Froebel kindergarten'),
                                  ('1896', "Freud's seduction paper"),
                                  ('1921', 'Hug-Hellmuth technique'),
                                  ('1947', 'Axline trade book')],
                                 'Children played before Vienna hired an hour; clinics arrived late to the nursery.'),
 'rpt-credential-as-object': ('The RPT credential',
                              [('1980s', 'Supervision hours'),
                               ('1990s', 'RPT naming'),
                               ('2000s', 'State lists'),
                               ('2010s', 'Online CE')],
                              'Registered Play Therapist as an association object with paperwork, not magic.'),
 'school-based-play-therapy': ('Play therapy in schools',
                               [('1960s', 'Counselor educators'),
                                ('1980s', 'Guidance models'),
                                ('2000s', 'CCPT school RCTs'),
                                ('2010s', 'Tiered services')],
                               'From counselor-education syllabi to district contracts — play crosses the school '
                               'door.'),
 'the-child-as-a-patient': ('When the child became a patient',
                            [('1909', 'Juvenile courts'),
                             ('1920s', 'Child guidance'),
                             ('1930s', 'Community clinics'),
                             ('1940s', 'War nurseries')],
                            'Child guidance, courts, and clinics that put a file on a minor before play had a name.'),
 'the-playroom-as-architecture': ('The playroom as architecture',
                                  [('1930s', 'Observation glass'),
                                   ('1947', 'Axline room list'),
                                   ('1960s', 'Filming one-way glass'),
                                   ('1980s', 'APT room norms')],
                                  'One-way glass, a sink, and a door that closes — rooms built as instruments.'),
 'the-sand-tray-as-an-object': ('The sand tray as object',
                                [('1929', 'Lowenfeld World Technique'),
                                 ('1950s', 'Kalff sandplay'),
                                 ('1980s', 'Catalog miniatures'),
                                 ('2000s', 'Credential trays')],
                                "Wood, sand, and miniatures as a profession's furniture — not a toy list."),
 'toys-class-and-the-catalog': ('Toys, class, catalog',
                                [('1930s', 'Mail-order dolls'),
                                 ('1960s', 'Flea-market rooms'),
                                 ('1980s', 'Publisher kits'),
                                 ('2000s', 'Amazon lists')],
                                'How catalogs and price tags quietly shaped what counted as a playroom.'),
 'who-was-left-out': ('Who was left out',
                      [('1920s', 'Segregated clinics'),
                       ('1960s', 'Urban renewal'),
                       ('1980s', 'Insurance gates'),
                       ('2020s', 'Telehealth divide')],
                      'A play-therapy history that only names Vienna, London, and Denton has a hole.')}

READER_SLUGS: dict[str, str] = {'how-to-read-a-play-therapy-claim': 'Reader essay — trials, credentials, and honest citations.',
 'living-people-public-documents': 'Reader essay — living authors and public documents only.',
 'map-to-sister-packs': 'Reader essay — where to send readers who wanted another lane.',
 'portraits-we-will-not-fake': 'Reader essay — no AI faces or scraped workshop photos.',
 'sister-packs-different-job': 'Reader essay — map to counseling and SLP sister packs.',
 'what-a-small-city-clinic-inherited': 'Reader essay — Southeast Arkansas heritage, not a service claim.',
 'what-this-folder-refuses': 'Reader essay — series fence and refusal list.',
 'what-we-opened': 'Reader essay — bibliography as honesty list.'}
CLEARED: dict[str, dict] = {}  # PD/CC rasters only; see PORTRAIT_SOURCES.md

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
  <rect x="0" y="0" width="360" height="8" fill="#4A6741"/>
  <text x="180" y="120" text-anchor="middle" font-family="Georgia, 'Palatino Linotype', serif" font-size="11" letter-spacing="0.14em" fill="#4A6741">WOW THERAPIES · PLAY THERAPY HISTORY</text>
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
  <rect x="0" y="0" width="{w}" height="6" fill="#4A6741"/>
  <text x="48" y="44" class="ink caps">Play therapy history</text>
  <text x="48" y="74" class="ink" font-size="22" font-weight="bold">{title}</text>
  <line class="rule" x1="{x0:.0f}" y1="210" x2="{x1:.0f}" y2="210"/>
{tick_block}
  <rect x="40" y="300" width="820" height="80" fill="#FFF" stroke="#1C1A17" stroke-width="0.6" opacity="0.92"/>
  <text x="52" y="322" class="muted caps">Caption</text>
  <text x="52" y="344" class="ink" font-size="12">{cap}</text>
  <text x="52" y="366" class="muted" font-size="11">Original SVG timeline (CC0). Slug: {slug}.</text>
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


def era_figure_html(slug: str, title: str, caption: str) -> str:
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


def write_pack_rights() -> None:
    lines = [
        "# Rights manifest — Play therapy history (WOW Therapies)",
        "",
        "Pack date: 14 September 2026. Authority for every binary likeness and editorial graphic.",
        "",
        "## Policy",
        "",
        "- **Never** AI-generated or synthetic historical faces.",
        "- Raster portraits only when cleared below (PD/CC with a live file-page license).",
        "- Typographic `plates/*/plate.svg` and `assets/era/*/lead-timeline.svg` are original editorial art (CC0).",
        "- Per-plate detail: `plates/<slug>/RIGHTS.md`. Era graphics: `GRAPHICS_INDEX.md`.",
        "",
        "## Cleared raster portraits",
        "",
    ]
    if not CLEARED:
        lines.append("_None shipped in this pass — see `PORTRAIT_SOURCES.md` (almost all figures are `no-portrait`)._")
    else:
        lines.append("| slug | file | license | source |")
        lines.append("| --- | --- | --- | --- |")
        for slug, meta in sorted(CLEARED.items()):
            lines.append(
                f"| {slug} | `{meta['file']}` | {meta['license']} | {meta['source_url']} |"
            )
    lines.extend(
        [
            "",
            "## Editorial SVG (CC0)",
            "",
            "| kind | path pattern |",
            "| --- | --- |",
            "| Era timeline | `assets/era/<slug>/lead-timeline.svg` |",
            "| Figure type plate | `plates/<slug>/plate.svg` |",
            "",
        ]
    )
    (ROOT / "RIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_graphics_index() -> None:
    rows_era = []
    for slug in sorted(ERA_SPECS):
        rows_era.append(
            f"| `{slug}` | `assets/era/{slug}/lead-timeline.svg` | ready | CC0 editorial |"
        )
    rows_fig = []
    for slug in sorted(FIGURE_SPECS):
        st = "cleared" if slug in CLEARED else "typographic"
        rows_fig.append(f"| `{slug}` | `plates/{slug}/plate.svg` | {st} | CC0 or see plate RIGHTS |")
    text = f"""# GRAPHICS_INDEX — play-therapy-history

Canonical register for lead graphics. Regenerate: `python3 graphics_pass.py`

## Era timelines (18)

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows_era)}

## Figure plates (19)

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows_fig)}

## Embed templates

- `embeds/era-figure-block.md`
- `embeds/figure-plate-block.md`

## Status legend

- **ready** — CC0 editorial SVG embedded in draft.
- **typographic** — No PD/CC likeness; name/dates plate only.
- **cleared** — PD/CC raster (none in default pass).
"""
    (ROOT / "GRAPHICS_INDEX.md").write_text(text, encoding="utf-8")


def build_assets() -> None:
    SHARED.mkdir(parents=True, exist_ok=True)
    PLATES.mkdir(parents=True, exist_ok=True)
    ERA_ASSETS.mkdir(parents=True, exist_ok=True)

    (SHARED / "reader-series-plate.svg").write_text(reader_series_svg(), encoding="utf-8")

    for slug, (title, events, caption) in ERA_SPECS.items():
        folder = ERA_ASSETS / slug
        folder.mkdir(parents=True, exist_ok=True)
        svg = era_timeline_svg(slug, title, events, caption)
        (folder / "lead-timeline.svg").write_text(svg, encoding="utf-8")

    for slug, (name, dates, seo) in FIGURE_SPECS.items():
        folder = PLATES / slug
        folder.mkdir(parents=True, exist_ok=True)
        if slug in CLEARED:
            meta = CLEARED[slug]
            dest = folder / meta.get("filename", "plate.jpg")
            if meta.get("url") and not dest.is_file():
                req = urllib.request.Request(meta["url"], headers={"User-Agent": UA})
                dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())
            write_plate_rights(folder / "RIGHTS.md", slug, name, dates, "cleared")
        else:
            (folder / "plate.svg").write_text(type_plate_svg(name, dates, seo), encoding="utf-8")
            write_plate_rights(folder / "RIGHTS.md", slug, name, dates, "typographic")



def reader_series_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="280" viewBox="0 0 900 280" role="img" aria-labelledby="title desc">
  <title id="title">WOW Therapies play therapy history — reader essay</title>
  <desc id="desc">Series template plate; no photograph or child stock art.</desc>
  <rect width="900" height="280" fill="#F7F2E8"/>
  <rect x="0" y="0" width="900" height="6" fill="#4A6741"/>
  <text x="48" y="52" font-family="Georgia, serif" font-size="11" letter-spacing="0.14em" fill="#4A6741">WOW THERAPIES · PLAY THERAPY HISTORY</text>
  <text x="48" y="100" font-family="Georgia, serif" font-size="26" font-weight="bold" fill="#1C1A17">Reader essay</text>
  <text x="48" y="136" font-family="Georgia, serif" font-size="15" fill="#5C564C">Educational history — not a protocol, not a toy list.</text>
  <text x="48" y="250" font-family="Georgia, serif" font-size="11" fill="#8a8278">Series template (CC0) · no AI faces · no stock children</text>
</svg>
"""


def reader_figure_html(slug: str, title: str, seo: str) -> str:
    cap = textwrap.shorten(seo, width=160, placeholder="…")
    return f"""
<!-- figure-id: {slug}.reader-series -->
<figure class="wow-figure wow-figure--reader">
  <img
    src="../assets/_shared/reader-series-plate.svg"
    alt="Series template for {title} — no photograph."
    width="900"
    height="280"
    loading="lazy"
  />
  <figcaption>
    <strong>{title}</strong> — {cap}
    <span class="figure-credit">Original series template (CC0). No AI-generated faces or children.</span>
  </figcaption>
</figure>
"""

def patch_drafts() -> None:
    needle = "not a substitute for care with a licensed clinician."
    for path in sorted(DRAFTS.glob("*.md")):
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
            fig = era_figure_html(slug, title, caption)
            front = re.sub(r"^portrait:.*$", "portrait: null", front, count=1, flags=re.M)
            if "lead_asset:" not in front:
                front += f'\nlead_asset: "assets/era/{slug}/lead-timeline.svg"'
            if "portrait_status:" not in front:
                front += "\nportrait_status: essay-only"
            else:
                front = re.sub(r"^portrait_status:.*$", "portrait_status: essay-only", front, count=1, flags=re.M)
            body = body[:insert_at] + "\n" + fig + body[insert_at:]
        elif fm.get("type") == "figure" and slug in FIGURE_SPECS:
            name, dates, seo = FIGURE_SPECS[slug]
            fig = figure_html(slug, name, dates, seo)
            status = "cleared" if slug in CLEARED else "typographic"
            ext = CLEARED.get(slug, {}).get("ext", "svg")
            portrait_path = f"plates/{slug}/plate.{ext}"
            front = re.sub(r"^portrait:.*$", f'portrait: "{portrait_path}"', front, count=1, flags=re.M)
            if "figure_dates:" not in front:
                front += f"\nfigure_dates: \"{dates}\""
            if "portrait_status:" not in front:
                front += f"\nportrait_status: {status}"
            else:
                front = re.sub(r"^portrait_status:.*$", f"portrait_status: {status}", front, count=1, flags=re.M)
            body = body[:insert_at] + "\n" + fig + body[insert_at:]
        elif fm.get("type") == "reader":
            title = fm.get("title", slug)
            seo = fm.get("meta_description", READER_SLUGS.get(slug, ""))
            fig = reader_figure_html(slug, title, seo)
            front = re.sub(r"^portrait:.*$", 'portrait: "assets/_shared/reader-series-plate.svg"', front, count=1, flags=re.M)
            if "portrait_status:" not in front:
                front += "\nportrait_status: series-template"
            else:
                front = re.sub(r"^portrait_status:.*$", "portrait_status: series-template", front, count=1, flags=re.M)
            body = body[:insert_at] + "\n" + fig + body[insert_at:]
        else:
            print(f"skip {path.name} (unknown slug {slug})")
            continue

        path.write_text(f"---\n{front}\n---\n{body}", encoding="utf-8")
        print(f"patched {path.name}")


def main() -> None:
    build_assets()
    write_pack_rights()
    write_graphics_index()
    patch_drafts()
    print("done")


if __name__ == "__main__":
    main()
