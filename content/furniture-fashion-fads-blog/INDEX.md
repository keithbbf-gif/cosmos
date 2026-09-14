# Furniture, fashion & fads — content pack (staged)

Editorial blog drafts with embedded schematic graphics (timelines, style cycles, comparison frames, retail-era charts).

| Doc | Purpose |
|-----|---------|
| [GRAPHICS_INDEX.md](GRAPHICS_INDEX.md) | Master list of slugs, SVG paths, captions |
| [GRAPHICS_STYLE.md](GRAPHICS_STYLE.md) | Design tokens and figure types |
| `graphics-manifest.json` | Machine-readable catalog |
| `articles/` | 44 magazine drafts with embedded `<figure>` blocks (`voice_check: human`) |
| `embeds/` | Copy-ready figure HTML per slug |
| `assets/<slug>/` | SVG figures |

Regenerate graphics: `python3 tools/fffb_graphics_build.py`

## Publish queue (Oct 2026 – Sep 2027)

Interior-fashion pillar from [`content/_seo/furniture-pillars.md`](../_seo/furniture-pillars.md). Full slug list: `MANIFEST.md` on the pack branch (not checked into this wire-only path).

| Month | SEO target | Staged slug | Status |
| --- | --- | --- | --- |
| 2026-10–2027-02 | (craft / woods months) | — | other furniture packs |
| 2027-03 | Fashion hub: one real room | `/fashion/` hub | **gap** (no hub draft); room essays e.g. `farmhouse-chic-cycle`, `conversation-pit-revival` are adjacent |
| 2027-04–2027-09 | (history / woods / craft rotation) | `fast-furniture-vs-fast-fashion` (Aug factory vs one-off angle) | partial in Aug only |
