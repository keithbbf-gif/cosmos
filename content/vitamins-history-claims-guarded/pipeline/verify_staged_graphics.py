#!/usr/bin/env python3
"""Verify staged vitamin-history graphics: SVG XML, raster registry, manifest."""

from __future__ import annotations

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = Path(__file__).resolve().parent
SOURCES = PIPELINE / "image_sources.json"
MANIFEST = ROOT / "staged" / "image_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_registry() -> dict:
    with SOURCES.open(encoding="utf-8") as f:
        return json.load(f)


def verify() -> list[str]:
    errors: list[str] = []
    reg = _load_registry()
    manifest_rows: list[dict] = []

    for entry in reg.get("svg", []):
        rel = entry["file"]
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing svg: {rel}")
            continue
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"invalid svg xml {rel}: {exc}")
        manifest_rows.append(
            {
                "id": entry["id"],
                "path": rel,
                "sha256": _sha256(path),
                "kind": entry.get("kind", "svg"),
            }
        )

    for entry in reg.get("images", []):
        rel = entry["file"]
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing image: {rel}")
            continue
        if path.stat().st_size < 1024:
            errors.append(f"suspiciously small image: {rel}")
        manifest_rows.append(
            {
                "id": entry["id"],
                "path": rel,
                "sha256": _sha256(path),
                "license": entry.get("license"),
                "draft_slug": entry.get("draft_slug"),
            }
        )

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps({"series": "vitamins-history-claims-guarded", "assets": manifest_rows}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("GRAPHICS_VERIFY PASS", len((ROOT / "staged" / "image_manifest.json").read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
