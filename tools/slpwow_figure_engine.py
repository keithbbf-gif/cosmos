#!/usr/bin/env python3
"""Generate SVG assets, embed snippets, RIGHTS rows, and patch articles."""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
EMBEDS = ROOT / "embeds"
ART = ROOT / "articles"
RIGHTS = ROOT / "RIGHTS.md"

PALETTE = {
    "paper": "#FAF9F7",
    "ink": "#1E293B",
    "muted": "#64748B",
    "card": "#FFFFFF",
    "rule": "#CBD5E1",
    "teal": ("#CCFBF1", "#0F766E"),
    "indigo": ("#E0E7FF", "#4338CA"),
    "amber": ("#FEF3C7", "#B45309"),
    "rose": ("#FFE4E6", "#BE123C"),
    "slate": ("#F1F5F9", "#475569"),
}

BEAT_THEME = {
    "ASLP-IC": "teal",
    "Medicare / CMS / ASHA": "indigo",
    "Licensure / school workforce": "amber",
    "Research": "rose",
    "Practice trends": "slate",
    "School SLP / caseload": "amber",
}

# slug, beat, file stem, svg title, desc, alt, caption lead, bullets, kind
GRAPHICS: list[dict] = []

PACK_FOOT = "SLPWOW — original editorial SVG. No photographs or AI faces."
PACK_EMBED_CREDIT = "SLPWOW — original editorial SVG. Not legal, billing, or clinical advice."
PACK_RIGHTS_HEADING = "Rights — SLPWOW editorial pack"

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def configure_pack(
    pack_root: Path,
    *,
    rights_heading: str,
    footnote: str,
    embed_credit: str,
) -> None:
    global ROOT, ASSETS, EMBEDS, ART, RIGHTS, PACK_FOOT, PACK_EMBED_CREDIT, PACK_RIGHTS_HEADING
    ROOT = pack_root.resolve()
    ASSETS = ROOT / "assets"
    EMBEDS = ROOT / "embeds"
    ART = ROOT / "articles"
    RIGHTS = ROOT / "RIGHTS.md"
    PACK_FOOT = footnote
    PACK_EMBED_CREDIT = embed_credit
    PACK_RIGHTS_HEADING = rights_heading


def parse_front(text: str) -> dict[str, str]:
    m = FRONT_RE.match(text)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def article_body(text: str) -> str:
    m = FRONT_RE.match(text)
    return text[m.end() :] if m else text


def _first_section_paragraphs(body: str) -> list[str]:
    m = re.search(r"^## .+\n(.*?)\n## ", body, re.S | re.M)
    chunk = m.group(1) if m else body
    paras: list[str] = []
    for block in re.split(r"\n\n+", chunk):
        block = block.strip()
        if not block or block.startswith("<figure"):
            continue
        if block.startswith("*") and block.endswith("*"):
            continue
        block = re.sub(r"\*\*([^*]+)\*\*", r"\1", block)
        block = re.sub(r"^#+ .+", "", block).strip()
        if not block:
            continue
        sent = re.split(r"(?<=[.!?])\s+", block)[0].strip()
        if len(sent) < 12:
            continue
        if len(sent) > 88:
            sent = sent[:85].rstrip() + "…"
        paras.append(sent)
        if len(paras) >= 4:
            break
    return paras


def infer_kind(slug: str, title: str, beat: str, desk: str) -> str:
    hay = f"{slug} {title}".lower()
    if beat == "ASLP-IC" and re.search(r"20\d{2}", title):
        return "timeline"
    if "versus" in hay or " is not " in title.lower() or "not a " in title.lower():
        return "compare"
    if slug.startswith("how-to") or hay.startswith("how "):
        return "flow"
    if desk == "cms" and re.search(r"\d", title):
        return "bars"
    if desk == "research" or beat == "Research":
        return "buckets"
    if "timeline" in hay or "calendar" in slug:
        return "timeline"
    return "card"


def build_specs_from_articles(desk_beats: dict[str, str], default_beat: str) -> list[dict]:
    specs: list[dict] = []
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_front(text)
        slug = fm.get("slug", "").strip()
        title = fm.get("title", slug).strip().strip('"')
        meta = fm.get("meta_description", title).strip().strip('"')
        desk = fm.get("desk", "").strip()
        beat = desk_beats.get(desk, default_beat)
        body = article_body(text)
        bullets = _first_section_paragraphs(body)
        if len(bullets) < 4:
            extras = [meta] + bullets
            bullets = []
            for line in extras:
                if line and line not in bullets:
                    bullets.append(line[:88] + ("…" if len(line) > 88 else ""))
                if len(bullets) >= 4:
                    break
        while len(bullets) < 4:
            bullets.append("Verify against the primary source before you share.")
        kind = infer_kind(slug, title, beat, desk)
        file_stem = slug[:48] + "-schematic"
        desc = meta if len(meta) > 40 else f"Educational schematic summarizing: {title}."
        alt = f"Educational infographic schematic: {title}. {meta[:120]}"
        caption = meta.rstrip(".") + "."
        specs.append(
            {
                "slug": slug,
                "beat": beat,
                "file": file_stem,
                "title": title[:90],
                "desc": desc[:220],
                "alt": alt[:240],
                "caption": caption[:200],
                "bullets": bullets[:4],
                "kind": kind,
            }
        )
    return specs


def run_pack(
    pack_root: Path,
    *,
    rights_heading: str,
    footnote: str,
    embed_credit: str,
    desk_beats: dict[str, str],
    default_beat: str,
) -> int:
    global GRAPHICS
    configure_pack(
        pack_root,
        rights_heading=rights_heading,
        footnote=footnote,
        embed_credit=embed_credit,
    )
    GRAPHICS = build_specs_from_articles(desk_beats, default_beat)
    for spec in GRAPHICS:
        write_svg(spec)
        write_embed(spec)
    write_rights()
    gaps = patch_articles()
    if gaps:
        print("PATCH GAPS:", *gaps, sep="\n")
        return 1
    print(f"OK: {len(GRAPHICS)} graphics in {pack_root.name}")
    return 0




def _esc(s: str) -> str:
    return html.escape(s, quote=False)


def _theme(beat: str) -> str:
    return BEAT_THEME.get(beat, "slate")


def _svg_styles(theme: str) -> str:
    band, accent = PALETTE[theme]
    return f"""
.bg {{ fill: {PALETTE['paper']}; }}
.title {{ font-family: Georgia, serif; font-size: 16px; font-weight: 600; fill: #1E293B; }}
.dek {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }}
.label {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #64748B; }}
.strong {{ font-family: system-ui, sans-serif; font-size: 12px; font-weight: 600; fill: #1E293B; }}
.card {{ fill: {PALETTE['card']}; stroke: {PALETTE['rule']}; stroke-width: 1; }}
.band {{ fill: {band}; }}
.accent {{ fill: {accent}; }}
.bullet {{ font-family: system-ui, sans-serif; font-size: 11px; fill: #1E293B; }}
.note {{ font-family: system-ui, sans-serif; font-size: 10px; fill: #64748B; }}
.spine {{ stroke: {accent}; stroke-width: 2; fill: none; }}
.node {{ fill: {accent}; }}
"""


def _body_default(bullets: list[str]) -> list[str]:
    lines: list[str] = []
    y0 = 148
    for i, b in enumerate(bullets[:4]):
        y = y0 + i * 28
        lines.append(f'  <circle cx="68" cy="{y - 4}" r="3" class="accent"/>')
        lines.append(f'  <text x="82" y="{y}" class="bullet">{_esc(b)}</text>')
    return lines


def _body_timeline(bullets: list[str]) -> list[str]:
    lines = [
        '  <line class="spine" x1="80" y1="200" x2="800" y2="200"/>',
    ]
    xs = [120, 280, 440, 600]
    for i, (x, b) in enumerate(zip(xs, bullets[:4])):
        lines.append(f'  <circle class="node" cx="{x}" cy="200" r="7"/>')
        lines.append(f'  <text x="{x}" y="178" text-anchor="middle" class="strong">{i + 1}</text>')
        wrapped = textwrap.wrap(b, width=22)[:2]
        for j, row in enumerate(wrapped):
            lines.append(
                f'  <text x="{x}" y="{228 + j * 14}" text-anchor="middle" class="label">{_esc(row)}</text>'
            )
    return lines


def _body_compare(bullets: list[str]) -> list[str]:
    left, right = bullets[:2], bullets[2:4]
    lines = [
        '  <rect class="band" x="56" y="140" width="370" height="200" rx="6"/>',
        '  <rect class="band" x="454" y="140" width="370" height="200" rx="6"/>',
        '  <text x="72" y="164" class="strong">Column A</text>',
        '  <text x="470" y="164" class="strong">Column B</text>',
    ]
    for i, b in enumerate(left):
        lines.append(f'  <text x="72" y="{188 + i * 22}" class="bullet">• {_esc(b)}</text>')
    for i, b in enumerate(right):
        lines.append(f'  <text x="470" y="{188 + i * 22}" class="bullet">• {_esc(b)}</text>')
    return lines


def _body_buckets(bullets: list[str]) -> list[str]:
    lines = []
    xs = [56, 232, 408, 584]
    for x, b in zip(xs, bullets[:4]):
        lines.append(f'  <rect class="band" x="{x}" y="150" width="168" height="170" rx="6"/>')
        wrapped = textwrap.wrap(b, width=18)[:3]
        for j, row in enumerate(wrapped):
            lines.append(f'  <text x="{x + 10}" y="{178 + j * 16}" class="label">{_esc(row)}</text>')
    return lines


def _body_bars(bullets: list[str]) -> list[str]:
    lines = []
    widths = [520, 420, 360, 300]
    for i, (b, w) in enumerate(zip(bullets[:4], widths)):
        y = 150 + i * 42
        lines.append(f'  <rect class="band" x="56" y="{y}" width="{w}" height="28" rx="4"/>')
        lines.append(f'  <text x="68" y="{y + 18}" class="bullet">{_esc(b)}</text>')
    return lines


def _body_flow(bullets: list[str]) -> list[str]:
    lines = []
    xs = [100, 300, 500, 700]
    for i, (x, b) in enumerate(zip(xs, bullets[:4])):
        if i:
            lines.append(f'  <line class="spine" x1="{xs[i-1]+40}" y1="210" x2="{x-40}" y2="210"/>')
        lines.append(f'  <rect class="band" x="{x - 70}" y="170" width="140" height="80" rx="6"/>')
        wrapped = textwrap.wrap(b, width=16)[:2]
        for j, row in enumerate(wrapped):
            lines.append(
                f'  <text x="{x}" y="{200 + j * 14}" text-anchor="middle" class="label">{_esc(row)}</text>'
            )
    return lines


BODY_BY_KIND = {
    "timeline": _body_timeline,
    "compare": _body_compare,
    "buckets": _body_buckets,
    "bars": _body_bars,
    "flow": _body_flow,
    "bridge": _body_compare,
    "map": _body_buckets,
    "stack": _body_compare,
    "card": _body_default,
}


def _svg_wrap(
    title: str,
    desc: str,
    headline: str,
    subline: str,
    bullets: list[str],
    beat: str,
    kind: str = "card",
    foot: str | None = None,
) -> str:
    if foot is None:
        foot = PACK_FOOT
    theme = _theme(beat)
    body_fn = BODY_BY_KIND.get(kind, _body_default)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 420" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{_esc(title)}</title>',
        f'  <desc id="desc">{_esc(desc)}</desc>',
        "  <defs><style>",
        _svg_styles(theme),
        "  </style></defs>",
        '  <rect class="bg" width="880" height="420"/>',
        f'  <text x="40" y="36" class="title">{_esc(headline)}</text>',
        f'  <text x="40" y="56" class="dek">{_esc(subline)}</text>',
        '  <rect class="card" x="40" y="76" width="800" height="300" rx="8"/>',
        '  <rect class="band" x="56" y="92" width="768" height="36" rx="4"/>',
        '  <rect class="accent" x="56" y="92" width="6" height="36" rx="2"/>',
        f'  <text x="72" y="116" class="strong">{_esc(beat)}</text>',
    ]
    lines.extend(body_fn(bullets))
    lines.append(f'  <text x="40" y="396" class="note">{_esc(foot)}</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_svg(spec: dict) -> Path:
    slug = spec["slug"]
    out_dir = ASSETS / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec['file']}.svg"
    subline = spec["desc"][:120] + ("…" if len(spec["desc"]) > 120 else "")
    path.write_text(
        _svg_wrap(
            spec["title"],
            spec["desc"],
            spec["title"],
            subline,
            spec["bullets"],
            spec["beat"],
            spec.get("kind", "card"),
            PACK_FOOT,
        ),
        encoding="utf-8",
    )
    return path


def write_embed(spec: dict) -> Path:
    EMBEDS.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]
    path = EMBEDS / f"{slug}.md"
    alt = spec["alt"]
    cap = spec["caption"]
    credit = PACK_EMBED_CREDIT
    body = textwrap.dedent(
        f"""# Embed — {slug}

```html
<figure class="slpwow-figure slpwow-figure--infographic" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="../assets/{slug}/{spec['file']}.svg"
    alt="{alt}"
    width="880"
    height="420"
    loading="lazy"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> {cap}
    <span class="figure-credit">{credit}</span>
  </figcaption>
</figure>
```
"""
    )
    path.write_text(body, encoding="utf-8")
    return path


def figure_html(spec: dict) -> str:
    credit = PACK_EMBED_CREDIT
    slug = spec["slug"]
    alt = spec["alt"]
    cap = spec["caption"]
    return textwrap.dedent(
        f"""
<figure class="slpwow-figure slpwow-figure--infographic" itemscope itemtype="https://schema.org/ImageObject">
  <img
    src="../assets/{slug}/{spec['file']}.svg"
    alt="{alt}"
    width="880"
    height="420"
    loading="lazy"
    itemprop="contentUrl"
  />
  <figcaption itemprop="caption">
    <strong>Figure 1.</strong> {cap}
    <span class="figure-credit">{credit}</span>
  </figcaption>
</figure>
"""
    ).strip()


def patch_articles() -> list[str]:
    missing: list[str] = []
    slug_to_spec = {g["slug"]: g for g in GRAPHICS}
    for path in sorted(ART.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.search(r'^slug:\s*"?([^"\n]+)"?\s*$', text, re.M)
        if not m:
            missing.append(f"{path.name}: no slug")
            continue
        slug = m.group(1).strip()
        spec = slug_to_spec.get(slug)
        if not spec:
            missing.append(f"{path.name}: no graphic spec for {slug}")
            continue
        if "<figure" in text:
            continue
        fig = figure_html(spec)
        # Insert after first ## section heading line
        sec = re.search(r"(^## .+\n)", text, re.M)
        if not sec:
            missing.append(f"{path.name}: no ## section")
            continue
        insert_at = sec.end()
        text = text[:insert_at] + "\n" + fig + "\n\n" + text[insert_at:]
        path.write_text(text, encoding="utf-8")
    return missing


def write_rights() -> None:
    lines = [
        f"# {PACK_RIGHTS_HEADING}",
        "",
        "Original editorial SVG schematics for draft articles in `articles/`. **No photographs, no AI-generated faces, no child likenesses.**",
        "",
        "| Asset path | Creator / rightsholder | License (this repo) | Credit (publish) | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for spec in GRAPHICS:
        rel = f"assets/{spec['slug']}/{spec['file']}.svg"
        lines.append(
            f"| `{rel}` | SLPWOW editorial | Practice may publish on slpwow.com | "
            f"“SLPWOW original schematic” | {spec['caption'][:80]}… |"
        )
    lines.extend(
        [
            "",
            "## Optional public-domain or Creative Commons rasters",
            "",
            "This wave ships **SVG only**. If editors later embed government maps or Wikimedia charts:",
            "",
            "| Source type | Example | Typical license | Rule |",
            "| --- | --- | --- | --- |",
            "| U.S. federal works | CMS, ASHA public PDF figures (cropped) | Often PD-USGov | Log URL + access date in `BIBLIOGRAPHY.md`; prefer linking out over raster embed. |",
            "| Wikimedia Commons | Historical SLP portraits | Varies (often PD-old) | Add a row here **before** embed; no AI colorization. |",
            "| Wellcome / LOC | Period engravings (equipment only) | Often CC BY 4.0 | Crop to objects; **no identifiable patients or children**. |",
            "",
            "## Excluded",
            "",
            "- AI-generated faces or “stock clinician” renders.",
            "- Patient photography, classroom photos, or any image with identifiable minors.",
            "- CompactConnect, CMS, or state board **logos** embedded as if endorsed — use text labels in schematics instead.",
            "",
        ]
    )
    RIGHTS.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate SLPWOW pack figures")
    parser.add_argument("pack_root", type=Path, help="Path to content pack root")
    args = parser.parse_args()
    desk_beats = {
        "literacy": "Practice trends",
        "asha": "Medicare / CMS / ASHA",
        "cms": "Medicare / CMS / ASHA",
        "compact": "ASLP-IC",
        "research": "Research",
    }
    name = args.pack_root.name
    if "caseload" in name:
        desk_beats = {}
        default = "School SLP / caseload"
        rights = "Rights — SLPWOW school caseload news pack"
        foot = "SLPWOW school caseload series — original editorial SVG. No photos or AI faces."
        credit = "SLPWOW school caseload series — original SVG. Not legal, billing, union, or clinical advice."
    elif "wave2" in name:
        default = "Practice trends"
        rights = "Rights — SLPWOW SLP News wave 2"
        foot = "SLPWOW SLP News wave 2 — original editorial SVG. No photographs or AI faces."
        credit = "SLPWOW SLP News wave 2 — original SVG. Not legal, billing, or clinical advice."
    else:
        default = "Practice trends"
        rights = f"Rights — {name}"
        foot = "SLPWOW — original editorial SVG. No photographs or AI faces."
        credit = "SLPWOW — original SVG. Not legal, billing, or clinical advice."
    return run_pack(
        args.pack_root,
        rights_heading=rights,
        footnote=foot,
        embed_credit=credit,
        desk_beats=desk_beats,
        default_beat=default,
    )


if __name__ == "__main__":
    raise SystemExit(main())
