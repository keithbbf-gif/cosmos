"""Staged graphics pack for vitamins-history-claims-guarded."""

from pathlib import Path
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content/vitamins-history-claims-guarded"
VERIFY = PACK / "pipeline/verify_staged_graphics.py"
EMBEDS = PACK / "staged/FIGURE_EMBEDS.md"


def test_verify_staged_graphics_pass():
    proc = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "GRAPHICS_VERIFY PASS" in proc.stdout


def test_rights_and_index_exist():
    assert (PACK / "RIGHTS.md").is_file()
    assert (PACK / "GRAPHICS_INDEX.md").is_file()
    assert (PACK / "staged/image_manifest.json").is_file()


def test_figure_embeds_use_semantic_html():
    text = EMBEDS.read_text(encoding="utf-8")
    figures = re.findall(r"<figure\b", text)
    assert len(figures) >= 10, len(figures)
    assert "<figcaption>" in text
    assert 'loading="lazy"' in text
    assert "alt=" in text
    assert "AI" not in text or "No AI" in (PACK / "RIGHTS.md").read_text(encoding="utf-8")


def test_manifest_matches_registry():
    reg = json.loads((PACK / "pipeline/image_sources.json").read_text(encoding="utf-8"))
    man = json.loads((PACK / "staged/image_manifest.json").read_text(encoding="utf-8"))
    reg_ids = {e["id"] for e in reg.get("images", []) + reg.get("svg", [])}
    man_ids = {e["id"] for e in man["assets"]}
    assert reg_ids == man_ids


def test_svgs_have_title_and_desc():
    for rel in (
        "staged/graphics/fig-01-discovery-timeline.svg",
        "staged/graphics/fig-02-naming-letters-map.svg",
        "staged/graphics/fig-03-commerce-statute-timeline.svg",
    ):
        root = ET.parse(PACK / rel).getroot()
        assert root.find("{http://www.w3.org/2000/svg}title") is not None, rel
        assert root.find("{http://www.w3.org/2000/svg}desc") is not None, rel
