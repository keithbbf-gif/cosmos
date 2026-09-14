#!/usr/bin/env python3
"""IMAGE+SEO pass: embed lead figures in three content packs (PD/CC + SVG)."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FRONT = re.compile(r"^(---\n.*?\n---\n)(.*)$", re.S)

# --- Commons downloads (pack-relative under assets/images/) ---
COMMONS: dict[str, tuple[str, str, str, str]] = {
    "cbt": (
        "Epictetus.jpg",
        "content/cbt-history-deep/assets/images/epictetus-engraving.jpg",
        "Public domain",
        "Later bust engraving of Epictetus (art object), via Wikimedia Commons",
    ),
}


def commons_url(filename: str) -> str:
    enc = urllib.parse.quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}"


def download_commons() -> None:
    meta_path = REPO / "content" / "_image_seo_download_meta.json"
    entries: list[dict] = []
    if meta_path.exists():
        entries = json.loads(meta_path.read_text(encoding="utf-8"))
    for key, (fname, rel, lic, credit) in COMMONS.items():
        dest = REPO / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = commons_url(fname)
        if dest.is_file() and dest.stat().st_size > 1000:
            print(f"SKIP existing {rel}")
        else:
            print(f"GET {fname}")
            req = urllib.request.Request(url, headers={"User-Agent": "COSMOS-image-seo/1.0"})
            data = urllib.request.urlopen(req, timeout=120).read()
            dest.write_bytes(data)
        entries.append({"key": key, "path": rel, "commons": fname, "license": lic, "credit": credit})
    meta_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def asset_relpath(md: Path, under_assets: str) -> str:
    """Compute relative path from md's directory to pack/assets/..."""
    parts = md.parts
    if "drafts" in parts:
        pack = md.parent.parent
    elif "articles" in parts:
        pack = md.parent.parent
    else:
        # stage-*/file.md
        idx = parts.index("act-mindfulness-therapy-history")
        pack = Path(*parts[: idx + 1])
    target = pack / "assets" / under_assets
    rel = Path(os.path.relpath(target, md.parent))
    return str(rel).replace("\\", "/")


import os


def figure_block(md: Path, src: str, alt: str, caption: str) -> str:
    return f"""
<figure class="blog-figure">
  <img src="{src}" alt="{alt}" width="720" loading="lazy" decoding="async" />
  <figcaption><strong>Figure.</strong> {caption}</figcaption>
</figure>
"""


def insert_after_lead(body: str, block: str) -> str:
    if "<figure" in body:
        return body
    needles = [
        "**Educational note.**",
        "**Disclaimer.**",
        "This draft does not treat",
        "This page does not treat",
    ]
    for n in needles:
        if n in body:
            idx = body.index(n)
            rest = body[idx:]
            end = rest.find("\n\n")
            if end == -1:
                return body + "\n\n" + block.strip() + "\n"
            at = idx + end + 2
            return body[:at] + block.strip() + "\n\n" + body[at:]
    parts = body.lstrip("\n").split("\n\n", 1)
    if len(parts) == 1:
        return body + "\n\n" + block.strip() + "\n"
    return parts[0] + "\n\n" + block.strip() + "\n\n" + parts[1]


def apply_file(md: Path, src: str, alt: str, caption: str) -> bool:
    raw = md.read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        return False
    fm, body = m.group(1), m.group(2)
    if "<figure" in body:
        return False
    new_body = insert_after_lead(body.lstrip("\n"), figure_block(md, src, alt, caption))
    md.write_text(fm + new_body, encoding="utf-8")
    return True


# --- CBT mappings (slug -> asset under assets/, alt, caption tail) ---
CBT_ERA: dict[str, tuple[str, str, str]] = {
    "stoic-sentences-before-the-clinic": (
        "images/epictetus-engraving.jpg",
        "Later engraved bust of Epictetus as historical art object",
        "Stoic sentences predate the clinic — caption the engraving as art, not a photograph. Public domain, via Wikimedia Commons.",
    ),
    "nimh-tdcrp-graph": (
        "shared/svg/nimh-tdcrp-three-columns.svg",
        "Schematic three-column layout for CBT, IPT, and imipramine on the NIMH TDCRP graph",
        "Layout mnemonic for Elkin 1989 — not reproduced outcome data. <em>Original schematic (CC0).</em>",
    ),
    "third-wave-nickname-2004": (
        "shared/svg/cbt-waves-timeline.svg",
        "Timeline of CBT document anchors from 1952 through the 2004 third-wave essay",
        "Nickname essays need dates, not lotus stock. <em>Schematic timeline; not to scale.</em>",
    ),
}
CBT_DEFAULT = (
    "shared/svg/series-type-lead.svg",
    "Neutral type lead for CBT history deepen essay",
    "Type treatment — no portrait licensed for this subject. <em>Original series art (CC0).</em>",
)

# Furniture slug -> asset
FURN: dict[str, tuple[str, str, str]] = {
    "quote-only-is-not-a-brush-off": ("shared/svg/schematic-series-type.svg", "Typeset custom furniture RFQ series lead", "Educational shop talk — not a price list. <em>Original typeset (CC0).</em>"),
    "rfq-is-a-job-not-an-email": ("shared/svg/schematic-rfq-one-page.svg", "Typeset blocks for a one-page furniture request for quote", "Object, dimensions, path, finish, freight, date on one page. <em>Original schematic (CC0).</em>"),
    "the-dealer-rfq-one-page": ("shared/svg/schematic-rfq-one-page.svg", "Dealer RFQ one-page layout with scope blocks", "Dealers still owe the shop a page, not a mood board. <em>Original schematic (CC0).</em>"),
    "the-homeowner-rfq-without-the-catalog": ("shared/svg/schematic-rfq-one-page.svg", "Homeowner RFQ layout without catalog SKUs", "No catalog number is not no information. <em>Original schematic (CC0).</em>"),
    "tape-on-the-wall-not-the-wish": ("images/kitchen-tape-measure-prep.jpg", "Tape measure in a bright kitchen prep setting", "Measure the wall you have, not the room on Pinterest. Photo: Shixart1985, Wikimedia Commons (CC BY 2.0)."),
    "dining-table-that-fits-the-room": ("shared/svg/schematic-dining-clearances.svg", "Top-down dining table with 36-inch chair zone and 42-inch pass aisle", "Chair pull-out and walk path before you lock length. <em>Original schematic (CC0).</em>"),
    "island-and-aisle-numbers": ("shared/svg/schematic-dining-clearances.svg", "Aisle and clearance schematic for built-in run dimensions", "Aisle numbers belong on the plan before the island depth. <em>Original schematic (CC0).</em>"),
    "the-path-through-the-house": ("shared/svg/schematic-delivery-path.svg", "Schematic delivery path from truck through stair landing to room", "Landings and soffits decide crate size. <em>Original schematic (CC0).</em>"),
    "lead-time-is-a-queue-not-a-stamp": ("shared/svg/schematic-lead-time-stack.svg", "Stack diagram of queue lumber mill finish buyouts and freight waits", "A rubber 12-week stamp hides six waits. <em>Original schematic (CC0).</em>"),
    "lumber-is-already-a-calendar": ("shared/svg/schematic-lead-time-stack.svg", "Lead-time stack emphasizing lumber and kiln wait", "Species and thickness are calendar events. <em>Original schematic (CC0).</em>"),
    "why-we-take-a-deposit": ("shared/svg/schematic-deposit-schedule.svg", "Deposit progress and balance blocks on a build timeline", "Deposit buys queue position, not the whole price. <em>Original schematic (CC0).</em>"),
    "deposit-is-not-the-whole-price": ("shared/svg/schematic-deposit-schedule.svg", "Payment schedule schematic for custom furniture builds", "Progress and balance still belong on the ack. <em>Original schematic (CC0).</em>"),
    "the-one-sitting-rfq-checklist": ("shared/svg/schematic-rfq-checklist.svg", "Checklist for object dimensions path finish freight date and money", "One sitting before you hit send. <em>Original typeset (CC0).</em>"),
}
FURN_DEFAULT = (
    "shared/svg/schematic-series-type.svg",
    "Custom furniture RFQ educational series typeset lead",
    "Typeset lead — shop photos stay in the private library until cleared. <em>Original typeset (CC0).</em>",
)

# ACT slug -> asset (path relative to pack assets/)
ACT_MAP: dict[str, tuple[str, str, str]] = {
    "third-wave-is-a-nickname": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Document timeline from 1975 IMS through 2008 OST meta-analysis",
        "Third wave is a nickname with dates attached. <em>Schematic; not effect sizes.</em>",
    ),
    "kabat-zinn-1979": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline highlighting 1979 MBSR hospital program anchor",
        "1979 is a program birth, not a trademark. <em>Schematic timeline.</em>",
    ),
    "hayes-before-the-1999-book": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline with 1999 Guilford ACT volume anchor",
        "Hayes before the blue book is still document history. <em>Schematic.</em>",
    ),
    "the-1999-guilford-volume": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline emphasizing 1999 ACT treatment volume",
        "Publisher objects are historical facts — jacket art stays © unless cleared. <em>Schematic.</em>",
    ),
    "teasdale-et-al-2000": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline with 2000 MBCT prevention trial anchor",
        "Journal mastheads beat scraped headshots. <em>Schematic.</em>",
    ),
    "hayes-2004-wave-essay": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline with 2004 third-wave family essay anchor",
        "The essay that named a wave — read the dates. <em>Schematic.</em>",
    ),
    "ost-2008": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Timeline with 2008 ACT outcomes meta-analysis anchor",
        "Meta-analyses are historical objects, not prescriptions. <em>Schematic.</em>",
    ),
    "ims-1975": (
        "shared/svg/act-societies-map.svg",
        "Schematic map pins for Barre IMS and related program cities",
        "IMS is a place on a map, not a stock cushion photo. <em>Schematic map.</em>",
    ),
    "american-zendo-after-1950": (
        "shared/svg/act-societies-map.svg",
        "Schematic map of western zendo and retreat program cities",
        "Post-1950 zendos are places and lineages — map, not a stock cushion. <em>Schematic map (CC0).</em>",
    ),
    "attention-is-older-than-a-clinic": (
        "shared/svg/mindfulness-west-document-timeline.svg",
        "Document timeline placing attention practices before clinic billing",
        "Attention is older than CPT codes — dates on documents, not outcome claims. <em>Schematic timeline.</em>",
    ),
}
ACT_DEFAULT = (
    "shared/svg/series-type-lead.svg",
    "ACT and mindfulness history series type lead",
    "Type treatment — no portrait licensed. <em>Original series art (CC0).</em>",
)


def slug_from_md(md: Path) -> str:
    text = md.read_text(encoding="utf-8")
    m = re.search(r"^slug:\s*([^\n]+)", text, re.M)
    if m:
        return m.group(1).strip().strip('"')
    m = re.search(r"^slug:\s*([^\n]+)", text)
    return m.group(1).strip() if m else md.stem.split("-", 1)[-1]


def run_cbt() -> int:
    root = REPO / "content/cbt-history-deep/drafts"
    n = 0
    for md in sorted(root.glob("*.md")):
        slug = slug_from_md(md)
        if slug in CBT_ERA:
            asset, alt, cap = CBT_ERA[slug]
        else:
            asset, alt, cap = CBT_DEFAULT
            if re.search(r"type:\s*figure", md.read_text(encoding="utf-8")):
                title_m = re.search(r'^title:\s*"([^"]+)"', md.read_text(encoding="utf-8"), re.M)
                if title_m:
                    alt = f"Type lead for essay: {title_m.group(1)}"
        src = asset_relpath(md, asset)
        if apply_file(md, src, alt, cap):
            n += 1
            print("cbt", md.name)
    return n


def run_furniture() -> int:
    root = REPO / "content/custom-furniture-rfq-sales/articles"
    n = 0
    for md in sorted(root.glob("*.md")):
        slug = slug_from_md(md)
        asset, alt, cap = FURN.get(slug, FURN_DEFAULT)
        src = asset_relpath(md, asset)
        if apply_file(md, src, alt, cap):
            n += 1
            print("furniture", md.name)
    return n


def run_act() -> int:
    root = REPO / "content/act-mindfulness-therapy-history"
    n = 0
    for md in sorted(root.glob("stage-*/*.md")):
        slug = slug_from_md(md)
        asset, alt, cap = ACT_MAP.get(slug, ACT_DEFAULT)
        src = asset_relpath(md, asset)
        if apply_file(md, src, alt, cap):
            n += 1
            print("act", md.relative_to(root))
    return n


def main() -> int:
    download_commons()
    total = run_cbt() + run_furniture() + run_act()
    print(f"embedded: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
