# Furniture, fashion & fads — content pack (staged)

Editorial blog drafts with embedded schematic graphics (timelines, style cycles, comparison frames, retail-era charts).

| Doc | Purpose |
|-----|---------|
| [GRAPHICS_INDEX.md](GRAPHICS_INDEX.md) | Master list of slugs, SVG paths, captions |
| [GRAPHICS_STYLE.md](GRAPHICS_STYLE.md) | Design tokens and figure types |
| [EDITOR_REPORT.md](EDITOR_REPORT.md) | Editor pass status and stub inventory |
| `graphics-manifest.json` | Machine-readable catalog |
| `articles/` | Draft stubs with embedded `<figure>` blocks |
| `embeds/` | Copy-ready figure HTML per slug |
| `assets/<slug>/` | SVG figures |

Regenerate graphics: `python3 tools/fffb_graphics_build.py`
