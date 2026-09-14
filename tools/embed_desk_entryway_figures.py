#!/usr/bin/env python3
"""Insert figure SEO blocks and frontmatter fields into desk-entryway drafts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "desks-hallway-entryway-furniture"
DRAFTS = PACK / "drafts"
MANIFEST = PACK / "assets" / "images" / "manifest.json"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
FIGURE_RE = re.compile(
    r"\n<!-- figure:commons -->\n<figure class=\"desk-entry-figure\">.*?</figure>\n",
    re.S,
)

ALT_BY_SLUG: dict[str, str] = {
    "why-this-folder": "American writing desk in a museum collection — staged history beside BBF collections, not a catalog hero",
    "what-a-desk-is": "Writing table with drawers — the desk job before marketing renamed every rectangle",
    "what-a-hall-is": "Victorian hall cupboard with hooks and storage — a hallway treated as a furnished room",
    "board-on-trestles": "Medieval trestle table scene from the Luttrell Psalter — board and legs before the fixed desk",
    "secretary-fall-front": "Fall-front secretary desk with closed lid — writing surface that locks the pigeonholes",
    "partner-desk": "Partners desk with two working faces sharing one carcass — banking-house form, not a big pedestal",
    "kneehole-pedestal": "Kneehole desk with marquetry — pedestal blocks with a void for the writer's knees",
    "roll-top": "Oak roll-top desk with tambour curtain closed — privacy lid, not a personality test",
    "wooton-indianapolis": "Wooton patent cabinet office secretary — Indiana desk with locking wings and cubbies",
    "campaign-desk": "Campaign-style desk with traveling furniture context — knock-down forms that survived a hold",
    "standing-to-write": "Standing desk with stool — counting-house height before sit-to-stand hardware",
    "typewriter-changed-the-top": "Desk with manual typewriter — machine height and carriage return changed the top",
    "l-and-u-return": "Early twentieth-century L-shaped desk layout — one rectangle was not enough surface",
    "computer-desk-scar": "Mid-century office desk with typewriter era hardware — ancestor of the beige-box apology desk",
    "twenty-nine-inches": "Writing table proportions in a museum photograph — seated height near twenty-nine to thirty inches",
    "depth-is-where-people-lie": "Library table depth in a museum view — long top invited company, not keyboard trays",
    "drawers-that-earn-keep": "Partner desk drawer bank — a drawer that will not take a folder is jewelry storage",
    "modesty-panel": "Art Deco desk with modesty panel and closed sides — knees hidden from the doorway",
    "when-to-refuse-a-desk": "Slant-front desk in a museum — beautiful form that still has to fit the room",
    "ladies-writing-desk": "Small writing desk in a period painting — a room-sized surface, not a gender label",
    "library-table-vs-desk": "Library table with generous top — desk that invited someone across the table",
    "lamp-and-the-left-hand": "Writer at a desk in a Dutch interior — lamp hand and writing hand negotiate space",
    "hall-as-a-room": "Hall cupboard with mirror and hooks — furnish the passage like a room, not a tunnel",
    "hall-stand-1840": "Renaissance Revival walnut hall stand — Victorian etiquette machine with mirror and drip pan",
    "pier-table-is-not-hall": "Pier table between windows in a parlor — not a console at the front door",
    "console-gave-up-a-side": "Console table against a wall — one long side surrendered to the architecture",
    "hall-tree-sat-down": "Entry hall hat stand with seat — coat rack that sat down, not a mudroom shoe bench",
    "calling-cards": "Wrought iron hall stand with umbrella well — social hardware for coats and weather",
    "umbrella-drip": "Victorian umbrella stand with drip tray — honest hardware for wet fabric",
    "mudroom-ate-the-hall": "Freestanding coat rack in a school entry — mudroom habits without Victorian volume",
    "closet-and-the-floor-plan": "Colonial interior passage — built-in storage changed what the hall had to carry",
    "settle-and-the-bench": "Oak settle bench — hall seating with a longer memory than a photo bench",
    "narrow-hall-tape": "Long narrow hall with tree and passage — tape the walkway before you buy romance",
    "hook-height": "Coat stand hook height in a furnished entry — kindness or slight for adults and children",
    "staging-the-entry": "Greek Revival parlor staging — traffic control is not the same as decorating",
    "bbf-collections-sit-beside-history": "Jasper Desk Company catalog page — Indiana factory desks beside history essays",
    "collection-page-names": "Historic desk catalog engraving — collection names must survive the century they borrow",
    "rta-is-a-door": "Queen Anne slant-front desk — ready-to-assemble is a door, not a sin against solid wood",
    "drop-zone": "Wall-mounted coat rack drop zone — keys and bags need a landing, not a sermon",
    "door-swing-before-romance": "Gilt console at the wall — measure door swing before the table owns the hall",
    "wood-in-a-hall": "Seventeenth-century monks bench — wood in a hall takes grit and wet, not study polish",
    "hardware-strangers-touch": "Hall cupboard hardware and mirror — strangers touch pulls before they touch your kitchen",
    "sequence-walk-in-to-leave": "Victorian hall stand sequence — hang, drip, mirror, then leave without blocking the door",
    "aftercare-water-and-grit": "Umbrella stand after wet weather — aftercare in a hall is water, salt, and grit",
}


def parse_fm(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"')
    return data, body


def meta_from_title(title: str) -> str:
    base = title.strip()
    if len(base) > 155:
        return base[:152] + "..."
    return f"{base}. Shop-floor history and design — staged beside BBF collections, not a SKU list."


def figure_block(row: dict[str, str], alt: str) -> str:
    src = f"../assets/images/{row['file']}"
    cap = (
        f"Figure 1. {alt.split(' — ')[0] if ' — ' in alt else alt}. "
        f"{row['source']}. {row['license']}. Full credits: RIGHTS.md."
    )
    return (
        "\n<!-- figure:commons -->\n"
        f'<figure class="desk-entry-figure">\n'
        f'<img src="{src}" alt="{alt}" width="760" loading="lazy" decoding="async" />\n'
        f"<figcaption>{cap}</figcaption>\n"
        f"</figure>\n"
    )


def inject_after_opening(body: str, block: str) -> str:
    body = FIGURE_RE.sub("\n", body)
    paras = re.split(r"\n\s*\n", body.strip(), maxsplit=1)
    if len(paras) == 1:
        return paras[0].strip() + "\n" + block
    return paras[0].strip() + "\n" + block + "\n" + paras[1].lstrip("\n")


def rebuild_fm(fm: dict[str, str], row: dict[str, str]) -> str:
    fm = dict(fm)
    fm["voice_check"] = "edited"
    fm["lane"] = "bbf-desks-hall"
    title = fm.get("title", row["slug"])
    fm["meta_description"] = meta_from_title(title)
    fm["figure_image"] = f"../assets/images/{row['file']}"
    order = [
        "id",
        "slug",
        "title",
        "meta_description",
        "stage",
        "status",
        "lane",
        "voice_check",
        "topics",
        "figure_image",
    ]
    lines = []
    for key in order:
        if key in fm:
            val = fm[key]
            if key in ("title", "meta_description") and " " in val:
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
    for key, val in fm.items():
        if key not in order:
            lines.append(f"{key}: {val}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def main() -> int:
    rows = {r["slug"]: r for r in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    errors: list[str] = []
    for path in sorted(DRAFTS.glob("*.md")):
        slug = None
        fm, body = parse_fm(path.read_text(encoding="utf-8"))
        slug = fm.get("slug")
        if not slug or slug not in rows:
            errors.append(f"{path.name}: slug {slug!r} not in manifest")
            continue
        row = rows[slug]
        alt = ALT_BY_SLUG.get(slug, f"Historic furniture photograph for {slug}")
        block = figure_block(row, alt)
        body = inject_after_opening(body, block)
        out = rebuild_fm(fm, row) + body
        if not out.endswith("\n"):
            out += "\n"
        path.write_text(out, encoding="utf-8")
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print(f"updated {len(list(DRAFTS.glob('*.md')))} drafts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
