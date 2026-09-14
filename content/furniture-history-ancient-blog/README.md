# Furniture history (ancient world) — staged blog pack

Editorial content only. **Not** part of COSMOS runtime or live tree.

## Layout

| Path | Purpose |
|------|---------|
| `INDEX.md` | Essay catalog (44 deep drafts) |
| `GRAPHICS_INDEX.md` | Figure inventory and reuse policy |
| `LICENSES.md` | External museum image policy; staged SVG license |
| `STYLE_GUIDE.md` | Caption and visual tone |
| `topics.json` | Source manifest for generator |
| `drafts/` | Markdown essays with embedded figures |
| `assets/<slug>/` | Per-essay SVG figure plates |
| `scripts/build_graphics_pack.py` | Regenerate figures and drafts from `topics.json` |

## Regenerate

```bash
python3 content/furniture-history-ancient-blog/scripts/build_graphics_pack.py
```

Figures are redrawn schematics (timelines, regional maps, typology diagrams, comparative plates)—museum-caption serious, no forged artifact photos.
