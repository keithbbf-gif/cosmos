#!/usr/bin/env python3
"""Write GRAPHICS_INDEX.md from specs and photo slots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
SPECS = json.loads((SCRIPT_DIR / "ffc_graphics_specs.json").read_text(encoding="utf-8"))
PHOTOS = json.loads((SCRIPT_DIR / "ffc_photo_slots.json").read_text(encoding="utf-8"))


def main() -> None:
    rows = []
    for slug in sorted(SPECS.keys()):
        spec = SPECS[slug]
        draft = next(ROOT.glob(f"*-{slug}.md"), None)
        draft_name = draft.name if draft else "(missing draft)"
        photo = "yes" if slug in PHOTOS else "—"
        rows.append(
            f"| `{slug}` | `{draft_name}` | `{spec['type']}` | `assets/{slug}/shop-diagram.svg` | {photo} |"
        )
    body = """---
title: Graphics index — furniture finishing chemistry
slug: graphics-index
status: draft
series: furniture-finishing-chemistry
---

# Graphics index

Staged assets for PR #303 image + SEO caption pass. SVGs are pack-authored (CC0). Rasters are PD/CC only; see `RIGHTS.md`.

| Slug | Draft | Diagram | SVG | Photo slot |
| --- | --- | --- | --- | --- |
"""
    body += "\n".join(rows) + "\n"
    (ROOT / "GRAPHICS_INDEX.md").write_text(body, encoding="utf-8")
    print(f"Wrote GRAPHICS_INDEX.md ({len(rows)} rows)")


if __name__ == "__main__":
    main()
