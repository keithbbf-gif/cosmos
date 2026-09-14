#!/usr/bin/env python3
"""Structural QA for content/arkansas-southern-woods-species/ image + SEO gates."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLATES = ROOT / "plates"
DIAGRAMS = ROOT / "assets" / "diagrams"
FIGURE_RE = re.compile(r'<figure class="asw-figure', re.I)
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

FIGURE_ARTICLES: dict[str, dict[str, str]] = {
    "01-white-oak-the-arkansas-workhorse.md": {"lead_figure": "species", "plate": "white-oak"},
    "02-white-oak-tyloses-barrels-tables.md": {"lead_figure": "diagram", "diagram": "white-oak-tyloses.svg"},
    "03-quartersawn-oak-southern-rays.md": {"lead_figure": "diagram", "diagram": "sawn-orientation.svg"},
    "04-southern-red-oak-not-the-catalog-name.md": {"lead_figure": "species", "plate": "southern-red-oak"},
    "07-oak-movement-arkansas-humidity.md": {"lead_figure": "diagram", "diagram": "shrink-radial-tangential.svg"},
    "13-shortleaf-the-arkansas-pine.md": {"lead_figure": "species", "plate": "shortleaf-pine"},
    "23-bald-cypress-delta-and-cache.md": {"lead_figure": "species", "plate": "bald-cypress"},
    "31-black-walnut-along-arkansas-rivers.md": {"lead_figure": "species", "plate": "black-walnut"},
    "37-black-cherry-boston-mountains.md": {"lead_figure": "species", "plate": "black-cherry"},
    "42-a-dining-table-in-five-woods.md": {"lead_figure": "diagram", "diagram": "arkansas-five-woods-janka.svg"},
    "45-moisture-and-why-southern-furniture-fails.md": {"lead_figure": "diagram", "diagram": "shrink-radial-tangential.svg"},
}

REQUIRED_WITH_FIGURE = ["meta_description", "lead_figure", "photo_status"]
AI_FACE = re.compile(
    r"(ai[- ]generated|synthetic (?:wood|grain|tree)|midjourney|stable diffusion)",
    re.I,
)


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


def main() -> int:
    errors: list[str] = []

    for plate_dir in PLATES.iterdir():
        if not plate_dir.is_dir():
            continue
        rights = plate_dir / "RIGHTS.md"
        if not rights.is_file():
            errors.append(f"missing RIGHTS.md for plate {plate_dir.name}")
        plate_files = list(plate_dir.glob("plate.*"))
        if not plate_files:
            errors.append(f"no plate.* in {plate_dir.name}")

    if not (DIAGRAMS / "RIGHTS.md").is_file():
        errors.append("missing assets/diagrams/RIGHTS.md")

    for fname, spec in FIGURE_ARTICLES.items():
        path = ROOT / fname
        if not path.is_file():
            errors.append(f"missing article {fname}")
            continue
        text = path.read_text(encoding="utf-8")
        front = parse_front(text)
        for key in REQUIRED_WITH_FIGURE:
            if key not in front:
                errors.append(f"{fname}: missing frontmatter {key}")
        if front.get("lead_figure") != spec["lead_figure"]:
            errors.append(f"{fname}: lead_figure should be {spec['lead_figure']}")
        if not FIGURE_RE.search(text):
            errors.append(f"{fname}: missing <figure class=\"asw-figure\"")
        if AI_FACE.search(text):
            errors.append(f"{fname}: banned AI/synthetic image language")

        if "plate" in spec:
            plate_path = PLATES / spec["plate"]
            if not plate_path.is_dir():
                errors.append(f"{fname}: unknown plate {spec['plate']}")

        if "diagram" in spec:
            if not (DIAGRAMS / spec["diagram"]).is_file():
                errors.append(f"{fname}: missing diagram {spec['diagram']}")

    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("OK: image + figure SEO gates passed for", len(FIGURE_ARTICLES), "lead-figure drafts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
