# Furniture, fashion & fads — content pack (staged)

Editorial blog drafts with embedded schematic graphics (timelines, style cycles, comparison frames, retail-era charts).

| Doc | Purpose |
|-----|---------|
| [GRAPHICS_INDEX.md](GRAPHICS_INDEX.md) | Master list of slugs, SVG paths, captions |
| [GRAPHICS_STYLE.md](GRAPHICS_STYLE.md) | Design tokens and figure types |
| `graphics-manifest.json` | Machine-readable catalog |
| `articles/` | 44 magazine drafts with embedded `<figure>` blocks (`voice_check: human`; stub line removed) |
| `embeds/` | Copy-ready figure HTML per slug |
| `assets/<slug>/` | SVG figures |

Regenerate graphics: `python3 tools/fffb_graphics_build.py`
