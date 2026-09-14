"""Staged graphics pack for transformers-public-history."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "transformers-public-history"
VERIFY = PACK / "pipeline" / "verify_staged_graphics.py"
EMBEDS = PACK / "staged" / "FIGURE_EMBEDS.md"
SVG_NS = "http://www.w3.org/2000/svg"

SVG_PATHS = (
    "staged/graphics/fig-01-first-public-timeline.svg",
    "staged/graphics/fig-02-transformer-stack-2017.svg",
    "staged/graphics/fig-03-attention-compute-flow.svg",
    "staged/graphics/fig-04-three-topologies-2018.svg",
    "staged/graphics/fig-05-context-mechanisms-timeline.svg",
    "staged/graphics/fig-06-sparse-hybrid-landscape.svg",
)

INLINE_DRAFTS = (
    PACK / "00-reading-rules.md",
    PACK / "01-attention-is-all-you-need-2017.md",
    PACK / "02-scaled-dot-product-attention.md",
    PACK / "09-three-topologies.md",
    PACK / "37-flashattention-2022.md",
    PACK / "48-hybrid-sparse-2024-2026.md",
)


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
    assert (PACK / "staged" / "image_manifest.json").is_file()
    rights = (PACK / "RIGHTS.md").read_text(encoding="utf-8")
    assert "No AI-generated images" in rights
    assert "No synthetic" in rights or "No AI" in rights


def test_figure_embeds_use_semantic_html():
    text = EMBEDS.read_text(encoding="utf-8")
    figures = re.findall(r"<figure\b", text)
    assert len(figures) >= 6, len(figures)
    assert "<figcaption>" in text
    assert 'loading="lazy"' in text
    assert "alt=" in text


def test_manifest_matches_registry():
    reg = json.loads((PACK / "pipeline" / "image_sources.json").read_text(encoding="utf-8"))
    man = json.loads((PACK / "staged" / "image_manifest.json").read_text(encoding="utf-8"))
    reg_ids = {e["id"] for e in reg.get("images", []) + reg.get("svg", [])}
    man_ids = {e["id"] for e in man["assets"]}
    assert reg_ids == man_ids


def test_svgs_have_title_and_desc():
    for rel in SVG_PATHS:
        root = ET.parse(PACK / rel).getroot()
        assert root.find(f"{{{SVG_NS}}}title") is not None, rel
        assert root.find(f"{{{SVG_NS}}}desc") is not None, rel


def test_key_drafts_embed_figures():
    for path in INLINE_DRAFTS:
        body = path.read_text(encoding="utf-8")
        assert "<figure" in body, path.name
        assert "<figcaption>" in body, path.name
        assert 'alt="' in body, path.name
