"""Validate bunk-beds-youth-furniture-history figure assets and markup."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

SERIES = Path(__file__).resolve().parents[1] / "content" / "bunk-beds-youth-furniture-history"


def test_schematic_svgs_are_well_formed() -> None:
    for svg in (SERIES / "images" / "schematics").glob("*.svg"):
        ET.parse(svg)


def test_figure_image_paths_exist() -> None:
    pattern = re.compile(r'<img\s+[^>]*src="([^"]+)"', re.I)
    missing: list[str] = []
    for md in SERIES.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for src in pattern.findall(text):
            if not (SERIES / src).is_file():
                missing.append(f"{md.name}: {src}")
    assert not missing, "missing figure assets:\n" + "\n".join(missing)


def test_rights_register_lists_schematics() -> None:
    rights = (SERIES / "RIGHTS.md").read_text(encoding="utf-8")
    for svg in (SERIES / "images" / "schematics").glob("*.svg"):
        rel = f"images/schematics/{svg.name}"
        assert rel in rights, f"{rel} not listed in RIGHTS.md"


def test_historical_images_listed_in_rights() -> None:
    rights = (SERIES / "RIGHTS.md").read_text(encoding="utf-8")
    for jpg in (SERIES / "images" / "historical").glob("*"):
        rel = f"images/historical/{jpg.name}"
        assert rel in rights, f"{rel} not listed in RIGHTS.md"
