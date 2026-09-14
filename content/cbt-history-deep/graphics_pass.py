#!/usr/bin/env python3
"""Image + SEO pass: era SVG timelines, typographic figure plates, RIGHTS.md, <figure> embeds.

PD/CC raster portraits only when listed in CLEARED (empty by default for this pack).
Never AI-generated faces.
"""
from __future__ import annotations

import re
import textwrap
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"
PLATES = ROOT / "plates"
ERA_ASSETS = ROOT / "assets" / "era"
SHARED = ROOT / "assets" / "_shared"
UA = "WOWTherapies-CBT-History-Deep/1.0 (educational; keith.bbf@gmail.com)"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FIGURE_RE = re.compile(
    r"\n<!-- figure-id:.*?-->\n<figure class=\"wow-figure.*?</figure>\n",
    re.S,
)

# Slug -> (display name, life dates, SEO epithet for figcaption)
FIGURE_SPECS: dict[str, tuple[str, str, str]] = {
    "aaron-temkin-beck": (
        "Aaron T. Beck",
        "1921–2021",
        "psychiatrist whose 1961 inventory and 1979 manual turned cognitive therapy into a workforce technology.",
    ),
    "albert-ellis-east-65th": (
        "Albert Ellis",
        "1913–2007",
        "founder who named rational emotive behavior therapy in 1955 and taught from a house on East 65th Street.",
    ),
    "judith-s-beck": (
        "Judith S. Beck",
        "1950–",
        "clinical psychologist who built the Beck Institute training shop after the 1994 founding.",
    ),
    "george-a-kelly": (
        "George A. Kelly",
        "1905–1967",
        "psychologist whose 1955 personal construct theory treated people as hypothesis testers.",
    ),
    "joseph-wolpe": (
        "Joseph Wolpe",
        "1915–1997",
        "South African–American psychiatrist who brought systematic desensitization into the behavior clinic.",
    ),
    "donald-meichenbaum": (
        "Donald Meichenbaum",
        "1940–",
        "cognitive-behavioral therapist known for stress inoculation and self-instructional training.",
    ),
    "arnold-a-lazarus": (
        "Arnold A. Lazarus",
        "1932–2013",
        "multimodal behavior therapist who argued techniques must match the person, not a single school badge.",
    ),
    "a-john-rush": (
        "A. John Rush",
        "1943–",
        "psychiatrist and co-author of the 1979 cognitive therapy of depression manual.",
    ),
    "david-m-clark": (
        "David M. Clark",
        "1952–",
        "Oxford psychologist behind IAPT-era protocols for anxiety and depression.",
    ),
    "david-h-barlow": (
        "David H. Barlow",
        "1942–",
        "anxiety researcher who unified empirically supported treatment manuals across disorders.",
    ),
    "marsha-linehan-cbt-dialectic": (
        "Marsha M. Linehan",
        "1943–",
        "psychologist who published dialectical behavior therapy as a cognitive-behavioral answer to chronic suicidality.",
    ),
    "steven-c-hayes": (
        "Steven C. Hayes",
        "1948–",
        "psychologist who named acceptance and commitment therapy and the 2004 third-wave address.",
    ),
    "zindel-segal-mbct": (
        "Zindel V. Segal",
        "1951–",
        "clinical psychologist who co-developed mindfulness-based cognitive therapy for depression relapse.",
    ),
    "jon-kabat-zinn": (
        "Jon Kabat-Zinn",
        "1944–",
        "molecular biologist who brought mindfulness into hospital stress-reduction clinics.",
    ),
    "jeffrey-e-young": (
        "Jeffrey E. Young",
        "1950–",
        "psychologist who formulated schema therapy as an extension of Beck's cognitive model.",
    ),
    "neil-s-jacobson": (
        "Neil S. Jacobson",
        "1949–2003",
        "researcher whose component studies and behavioral activation trials challenged how CBT was packaged.",
    ),
    "christine-a-padesky": (
        "Christine A. Padesky",
        "1950–",
        "cognitive therapist and trainer known for collaborative case conceptualization workshops.",
    ),
    "david-d-burns-feeling-good": (
        "David D. Burns",
        "1942–",
        "psychiatrist whose 1980 *Feeling Good* brought Beck's ideas to bookstore readers.",
    ),
    "dianne-l-chambless": (
        "Dianne L. Chambless",
        "1948–",
        "clinical psychologist who helped define empirically supported therapy lists in the 1990s.",
    ),
    "philip-c-kendall": (
        "Philip C. Kendall",
        "1950–",
        "child CBT researcher known for Coping Cat and youth anxiety trials.",
    ),
    "edna-b-foa": (
        "Edna B. Foa",
        "1937–",
        "anxiety researcher who developed prolonged exposure protocols for PTSD.",
    ),
    "patricia-a-resick": (
        "Patricia A. Resick",
        "1949–",
        "trauma psychologist who built cognitive processing therapy for survivors.",
    ),
    "stefan-g-hofmann": (
        "Stefan G. Hofmann",
        "1957–",
        "Boston psychologist who synthesized process-based and third-wave cognitive therapy research.",
    ),
    "adrian-wells": (
        "Adrian Wells",
        "1956–",
        "British psychologist associated with metacognitive therapy for worry and rumination.",
    ),
}

# Era slug -> (short title, list of (year, label), caption SEO)
ERA_SPECS: dict[str, tuple[str, list[tuple[str, str]], str]] = {
    "stoic-sentences-before-the-clinic": (
        "Stoic sentences before the clinic",
        [
            ("~125", "Epictetus / Arrian"),
            ("180", "Marcus Aurelius notes"),
            ("1955", "Ellis names REBT"),
            ("1962", "Ellis quotes Enchiridion"),
            ("2010s", "Stoic revival blogs"),
        ],
        "How a first-century handbook sentence traveled into mid-century American therapy without becoming a worksheet.",
    ),
    "adler-cognitive-timber": (
        "Adler's cognitive timber",
        [
            ("1912", "Individual psychology"),
            ("1927", "Inferiority / goals"),
            ("1955", "Kelly constructs"),
            ("1963", "Beck thinking papers"),
        ],
        "Individual psychology as cognitive precursor — goals and fictions before the Beck inventory.",
    ),
    "kelly-personal-constructs-1955": (
        "Personal constructs, 1955",
        [
            ("1955", "*Psychology of Personal Constructs*"),
            ("1955", "Ellis REBT begins"),
            ("1967", "Beck depression book"),
        ],
        "George Kelly's 1955 two-volume theory beside Ellis's naming year.",
    ),
    "eysenck-1952-gauntlet": (
        "Eysenck's 1952 gauntlet",
        [
            ("1952", "Psychotherapy outcome paper"),
            ("1960s", "Behavior therapy trials"),
            ("1977", "EST debates"),
        ],
        "Hans Eysenck's challenge that pushed behavior therapists to measure outcomes.",
    ),
    "first-wave-behavior-clinic": (
        "First-wave behavior clinic",
        [
            ("1920s", "Watson era"),
            ("1958", "Wolpe desensitization"),
            ("1960s", "Token economies"),
        ],
        "Behavior therapy enters the hospital without retelling forbidden child experiments.",
    ),
    "ellis-names-rebt-1955": (
        "Ellis names a therapy, 1955",
        [
            ("1955", "Rational therapy named"),
            ("1957", "Adler debt paper"),
            ("1962", "*Reason and Emotion*"),
        ],
        "Albert Ellis's 1955 naming as a New York public argument, not a Stoic class.",
    ),
    "beck-leaves-the-couch": (
        "Beck leaves the couch",
        [
            ("1950s", "Psychoanalytic training"),
            ("1961", "Depression inventory"),
            ("1963–64", "Thinking papers"),
        ],
        "Aaron Beck's Philadelphia pivot from analytic hypotheses to testable sentences.",
    ),
    "depression-book-1967": (
        "The 1967 depression book",
        [
            ("1967", "*Depression* (Hoeber)"),
            ("1976", "*Emotional Disorders*"),
            ("1979", "Workforce manual"),
        ],
        "Beck's 1967 colleague volume before the Guilford manual era.",
    ),
    "depression-manual-1979": (
        "The 1979 depression manual",
        [
            ("1979", "Guilford manual"),
            ("1980", "CTS scale"),
            ("1980", "*Feeling Good*"),
        ],
        "How a depression sequence became trainable workforce technology.",
    ),
    "dsm-iii-countable-object": (
        "DSM-III and the countable object",
        [
            ("1980", "DSM-III"),
            ("1987", "DSM-III-R"),
            ("1994", "DSM-IV"),
        ],
        "Diagnostic manuals as billing and research objects — not cover art for blogs.",
    ),
    "nimh-tdcrp-graph": (
        "Three schools on one NIMH graph",
        [
            ("1989", "TDCRP published"),
            ("1990s", "Medication + CBT trials"),
            ("2006", "STAR*D"),
        ],
        "NIMH depression trials that plotted cognitive, behavioral, and pharmacologic arms together.",
    ),
    "chambless-est-lists": (
        "Empirically supported treatment lists",
        [
            ("1993", "Chambless criteria"),
            ("1995", "APA Division 12"),
            ("1998", "EST task force"),
        ],
        "How lists of supported therapies reshaped training and managed care arguments.",
    ),
    "managed-care-six-sessions": (
        "Managed care and six sessions",
        [
            ("1980s", "Utilization review"),
            ("1990s", "Six-session authorizations"),
            ("2000s", "Manualized brief CBT"),
        ],
        "Insurance shape as a cousin of the worksheet — not a clinical theory.",
    ),
    "third-wave-nickname-2004": (
        "The third-wave nickname, 2004",
        [
            ("1990s", "ACT / DBT / MBCT"),
            ("2004", "Hayes address"),
            ("2010s", "Mindfulness clinics"),
        ],
        "Why acceptance-based therapies got a wave nickname in *Behavior Therapy*.",
    ),
    "behavioral-activation-return": (
        "Behavioral activation returns",
        [
            ("1996", "Jacobson component study"),
            ("2001", "BA vs CT trial"),
            ("2010s", "IAPT low-intensity BA"),
        ],
        "Behavioral activation's return as a challenge to what counted as the active ingredient.",
    ),
    "iapt-political-object": (
        "IAPT as a political object",
        [
            ("2006", "Layard / Clark"),
            ("2008", "IAPT rollout"),
            ("2010s", "Stepped care"),
        ],
        "England's Improving Access to Psychological Therapies as policy, not a room photograph.",
    ),
    "computerized-cbt-and-apps": (
        "Computerized CBT and apps",
        [
            ("2000s", "Beating the Blues"),
            ("2010s", "App stores"),
            ("2020s", "Telehealth surge"),
        ],
        "Digital delivery without screenshots you do not own.",
    ),
    "critiques-worksheet-could-not-hear": (
        "Critiques the worksheet could not hear",
        [
            ("1970s", "Feminist therapy"),
            ("1990s", "Power in the room"),
            ("2000s", "Liberation critiques"),
        ],
        "Social and political arguments that cognitive manuals struggled to absorb.",
    ),
    "process-based-cbt-family-fight": (
        "Process-based CBT family fight",
        [
            ("2010s", "Transdiagnostic models"),
            ("2020", "Hofmann & Hayes process-based"),
            ("2020s", "Mechanism trials"),
        ],
        "Whether CBT should be packaged as protocols or processes.",
    ),
    "after-beck-2021": (
        "After Beck, 2021",
        [
            ("1994", "Beck Institute"),
            ("2021", "Beck death"),
            ("2020s", "CT-R extensions"),
        ],
        "What survived the founder after November 2021 — institutes, scales, arguments.",
    ),
}

CLEARED: dict[str, dict] = {}  # portrait_id -> download metadata; empty unless PD/CC row added


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
  <rect x="0" y="0" width="360" height="8" fill="#6B2D3E"/>
  <text x="180" y="120" text-anchor="middle" font-family="Georgia, 'Palatino Linotype', serif" font-size="11" letter-spacing="0.14em" fill="#6B2D3E">WOW THERAPIES · CBT HISTORY</text>
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
  <text x="48" y="44" class="ink caps">CBT history deepen</text>
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
        "# Rights manifest — CBT history deepen (WOW Therapies)",
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
    text = f"""# GRAPHICS_INDEX — cbt-history-deep

Canonical register for lead graphics. Regenerate: `python3 graphics_pass.py`

## Era timelines (20)

| Slug | File | Status | Rights |
| --- | --- | --- | --- |
{chr(10).join(rows_era)}

## Figure plates (24)

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
