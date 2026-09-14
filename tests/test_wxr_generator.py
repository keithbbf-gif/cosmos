#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for tools.wxr draft-import generator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.wxr.frontmatter import parse_markdown
from tools.wxr.generator import build_post_exports, generate_wxr, render_wxr
from tools.wxr.manifest import load_manifest


SAMPLE = ROOT / "content/_ops/wxr/samples/figroots-blog/2026-03-01-brown-turkey-leaf-spot.md"
MANIFEST = ROOT / "content/_ops/wxr/manifest.toml"


def test_parse_strips_voice_check():
    text = SAMPLE.read_text(encoding="utf-8")
    parsed = parse_markdown(text)
    assert "voice_check" not in parsed.meta
    assert "voice_check" in parsed.stripped_keys
    assert parsed.meta["title"] == "Brown Turkey fig leaf spot"


def test_figure_paths_collected():
    manifest = load_manifest(MANIFEST, ROOT)
    pack = next(p for p in manifest.packs if p.id == "figroots-blog")
    exports = build_post_exports(manifest, pack, use_samples=True)
    assert len(exports) >= 1
    paths = exports[0].figure_paths
    assert "content/figroots-blog/media/cercospora-leaf.jpg" in paths


def test_wxr_is_draft_only():
    manifest = load_manifest(MANIFEST, ROOT)
    pack = next(p for p in manifest.packs if p.id == "figroots-blog")
    exports = build_post_exports(manifest, pack, use_samples=True)
    xml = render_wxr(pack, exports)
    assert "<wp:status>draft</wp:status>" in xml
    assert "<wp:status>publish</wp:status>" not in xml
    assert "_cosmos_media_notes" in xml
    assert "cosmos-media-notes" in xml


def test_manifest_lists_ten_packs():
    manifest = load_manifest(MANIFEST, ROOT)
    assert len(manifest.packs) == 10
    ids = {p.id for p in manifest.packs}
    assert "ai-history-retrospective" in ids
    assert "figroots-blog" in ids


def test_manifest_posts_glob_under_content_pack_root():
    manifest = load_manifest(MANIFEST, ROOT)
    for pack in manifest.packs:
        assert "content/packs/" not in pack.posts_glob
        assert pack.posts_glob == f"content/{pack.id}/posts/**/*.md"


def test_cli_dry_run_json():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.wxr",
            "generate",
            "figroots-blog",
            "--dry-run",
            "--root",
            str(ROOT),
            "--manifest",
            str(MANIFEST),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["dry_run"] is True
    assert data["post_count"] >= 1
    assert data["posts"][0]["stripped_keys"] == ["voice_check"]


def test_generate_writes_file():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.wxr.xml"
        result = generate_wxr(
            "figroots-blog",
            manifest_path=MANIFEST,
            repo_root=ROOT,
            output=out,
            use_samples=True,
        )
        assert result.output_path == out
        assert out.exists()
        body = out.read_text(encoding="utf-8")
        assert "Brown Turkey fig leaf spot" in body
