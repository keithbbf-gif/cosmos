#!/usr/bin/env python3
"""Validate AI-history graphics against the WRITER + GRAPHICS (#247) contract.

Fail-closed on:
- missing viewBox / <desc> / well-formed XML
- generated / synthetic / Midjourney / DALL-E / Stable Diffusion / Flux
- remote <image href="http...">
- portrait plates that claim a likeness without a PORTRAIT_SOURCES.md raster
- figure-*/portrait-plate.svg that still say 'rights not cleared' after COPY
  has cleared Turing / McCarthy / Minsky
- missing required shared IDs
- missing GRAPHICS_INDEX.md row for a figure id
- embed files that do not use the two-line contract and article-relative paths
- COPY articles missing their graphics_slug (and required in-body embeds)
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
INDEX = ROOT / "GRAPHICS_INDEX.md"
EMBEDS = ROOT / "staged" / "embeds"
PORTRAIT_SOURCES = ROOT / "PORTRAIT_SOURCES.md"

FORBIDDEN_SUBSTRINGS = (
    "midjourney",
    "dall-e",
    "dalle",
    "stable diffusion",
    "flux",
    "ai generated",
    "ai-generated",
    "synthetic portrait",
    "generated face",
)

REQUIRED_SHARED_IDS = ("G-ERA-001", "G-WIN-001", "G-PAR-001")

# COPY-cleared rasters (see PORTRAIT_SOURCES.md). Plates must embed these
# local files and must not keep the hatch / 'rights not cleared' language.
CLEARED_PLATES = {
    "figure-alan-turing": {
        "raster": "portraits/alan-turing.jpg",
        "require": ("likeness reproduced", "princeton"),
    },
    "figure-john-mccarthy": {
        "raster": "portraits/john-mccarthy.jpg",
        "require": ("likeness reproduced", "stanford"),
    },
    "figure-marvin-minsky": {
        "raster": "portraits/marvin-minsky.jpg",
        "require": ("likeness reproduced", "olpc"),
    },
}

UNCLEANED_PLATE_REQUIRE = ("rights not cleared", "no likeness reproduced")

# COPY slug (this tree) → graphics slug (PR #247 folders / embed packs).
COPY_SLUG_MAP = {
    "essays/00-series-overview.md": "00-series-overview",
    "essays/before-the-machines-thought.md": "pre-1956-origins",
    "essays/cybernetics-and-the-macy-years.md": "pre-1956-origins",
    "essays/dartmouth-1956.md": "dartmouth-1956",
    "essays/the-symbolic-bet.md": "symbolic-ai-era",
    "essays/perceptrons-and-the-first-winter.md": "first-ai-winter",
    "essays/winters-and-summers.md": "first-ai-winter",
    "essays/expert-systems-summer.md": "expert-systems-1980s",
    "essays/connectionist-revival.md": "connectionist-revival",
    "essays/statistical-turn.md": "statistical-ml-1990s",
    "essays/imagenet-moment.md": "deep-learning-renaissance",
    "essays/attention-and-transformers.md": "transformers-and-foundation-models",
    "essays/llms-2018-2026.md": "transformers-and-foundation-models",
    "profiles/alan-turing.md": "figure-alan-turing",
    "profiles/john-mccarthy.md": "figure-john-mccarthy",
    "profiles/marvin-minsky.md": "figure-marvin-minsky",
}

REQUIRED_BODY_EMBEDS = {
    "essays/00-series-overview.md": (
        "era-timeline-pre1956-2026.svg",
        "paradigm-comparison.svg",
        "ai-winter-summer-schematic.svg",
    ),
    "essays/before-the-machines-thought.md": (
        "pre-1956-origins/timeline.svg",
        "pre-1956-origins/labs-schools.svg",
    ),
    "essays/cybernetics-and-the-macy-years.md": (
        "pre-1956-origins/labs-schools.svg",
    ),
    "essays/dartmouth-1956.md": ("dartmouth-1956/timeline.svg",),
    "essays/the-symbolic-bet.md": ("symbolic-ai-era/labs-schools.svg",),
    "essays/perceptrons-and-the-first-winter.md": ("ai-winter-summer-schematic.svg",),
    "essays/winters-and-summers.md": ("ai-winter-summer-schematic.svg",),
    "essays/expert-systems-summer.md": ("era-timeline-pre1956-2026.svg",),
    "essays/connectionist-revival.md": ("paradigm-comparison.svg",),
}

REQUIRED_EMBED_PACKS = (
    "00-series-overview.md",
    "pre-1956-origins.md",
    "dartmouth-1956.md",
    "symbolic-ai-era.md",
    "first-ai-winter.md",
    "expert-systems-1980s.md",
    "connectionist-revival.md",
    "statistical-ml-1990s.md",
    "deep-learning-renaissance.md",
    "transformers-and-foundation-models.md",
    "figure-alan-turing.md",
    "figure-john-mccarthy.md",
    "figure-marvin-minsky.md",
)

TEMPLATE_SKIP = {"archival-defs.svg"}
HTTP_IMAGE = re.compile(r"""<image[^>]+(?:href|xlink:href)=["']https?://""", re.I)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def svg_files() -> list[Path]:
    skip_dirs = {"_templates", "portraits", "retired"}
    return sorted(
        p for p in ASSETS.rglob("*.svg") if skip_dirs.isdisjoint(p.parts)
    )


def check_forbidden_language(path: Path, text: str) -> None:
    lowered = text.lower()
    for needle in FORBIDDEN_SUBSTRINGS:
        if needle in lowered:
            fail(f"{path}: forbidden language '{needle}'")


def check_svg_basics(path: Path, text: str) -> None:
    if 'viewBox="' not in text and "viewBox='" not in text:
        fail(f"{path}: missing viewBox")
    if HTTP_IMAGE.search(text):
        fail(f"{path}: remote <image> href is forbidden")
    if path.name not in TEMPLATE_SKIP and "<desc" not in text:
        fail(f"{path}: missing <desc>")
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        fail(f"{path}: XML parse: {exc}")


def check_shared_ids() -> None:
    shared = ASSETS / "shared"
    if not shared.is_dir():
        fail("assets/shared/ missing")
    blob = "\n".join(p.read_text(encoding="utf-8") for p in shared.glob("*.svg"))
    for gid in REQUIRED_SHARED_IDS:
        if gid not in blob:
            fail(f"shared SVG set missing id {gid}")


def check_index_rows() -> None:
    if not INDEX.is_file():
        fail("GRAPHICS_INDEX.md missing")
    text = INDEX.read_text(encoding="utf-8")
    for gid in REQUIRED_SHARED_IDS:
        if gid not in text:
            fail(f"GRAPHICS_INDEX.md missing {gid}")
    for slug in CLEARED_PLATES:
        if slug not in text:
            fail(f"GRAPHICS_INDEX.md missing cleared plate {slug}")
    for copy_path, gslug in COPY_SLUG_MAP.items():
        if gslug not in text:
            fail(f"GRAPHICS_INDEX.md missing graphics slug {gslug} (from {copy_path})")


def check_portrait_plate(path: Path, text: str) -> None:
    slug = path.parent.name
    lowered = text.lower()
    if slug in CLEARED_PLATES:
        spec = CLEARED_PLATES[slug]
        raster = spec["raster"]
        if raster not in text.replace("\\", "/"):
            fail(f"{path}: cleared plate must embed {raster}")
        if "<image" not in lowered:
            fail(f"{path}: cleared plate must use a local <image>")
        if "rights not cleared" in lowered or "no likeness reproduced" in lowered:
            fail(f"{path}: cleared plate still carries hatch / uncleared language")
        for needle in spec["require"]:
            if needle not in lowered:
                fail(f"{path}: cleared plate missing credit language '{needle}'")
        raster_path = ASSETS / raster
        if not raster_path.is_file():
            fail(f"{path}: raster {raster} not on disk")
        return

    if "<image" in lowered:
        fail(f"{path}: uncleared plate must not embed a likeness")
    for needle in UNCLEANED_PLATE_REQUIRE:
        if needle not in lowered:
            fail(f"{path}: uncleared plate missing '{needle}'")


def check_embeds() -> None:
    if not EMBEDS.is_dir():
        fail("staged/embeds/ missing")
    for name in REQUIRED_EMBED_PACKS:
        path = EMBEDS / name
        if not path.is_file():
            fail(f"staged/embeds/{name} missing")
        text = path.read_text(encoding="utf-8")
        if "![" not in text or "*Figure " not in text:
            fail(f"{path}: embed missing two-line figure contract")
        if "../../assets/" in text:
            fail(f"{path}: embed still uses graphics-branch relative depth")
        if "../assets/" not in text:
            fail(f"{path}: embed must use article-relative ../assets/ path")


def check_portrait_sources_for_cleared() -> None:
    if not PORTRAIT_SOURCES.is_file():
        fail("PORTRAIT_SOURCES.md missing")
    text = PORTRAIT_SOURCES.read_text(encoding="utf-8")
    for name in ("Alan Turing", "John McCarthy", "Marvin Minsky"):
        if name not in text:
            fail(f"PORTRAIT_SOURCES.md missing {name}")


def check_copy_alignment() -> None:
    for rel, gslug in COPY_SLUG_MAP.items():
        path = ROOT / rel
        if not path.is_file():
            fail(f"COPY article missing: {rel}")
        text = path.read_text(encoding="utf-8")
        if f"graphics_slug: {gslug}" not in text:
            fail(f"{rel}: front matter must include graphics_slug: {gslug}")
        for fragment in REQUIRED_BODY_EMBEDS.get(rel, ()):
            if fragment not in text:
                fail(f"{rel}: missing required figure embed {fragment}")


def main() -> None:
    if not ASSETS.is_dir():
        fail("assets/ missing")
    counted = 0
    for path in svg_files():
        counted += 1
        text = path.read_text(encoding="utf-8")
        check_forbidden_language(path, text)
        check_svg_basics(path, text)
        if path.name == "portrait-plate.svg" and path.parent.name.startswith("figure-"):
            check_portrait_plate(path, text)
    check_shared_ids()
    check_index_rows()
    check_embeds()
    check_portrait_sources_for_cleared()
    check_copy_alignment()
    print(f"OK: graphics validation passed ({counted} production SVGs)")


if __name__ == "__main__":
    main()
