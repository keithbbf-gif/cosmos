# Graphics index — ACT / mindfulness history

Original SVG only for timelines and maps. Portraits: PD/CC per `plates/*/RIGHTS.md` or honest type/placeholder.

## Shared assets

| File | Use |
| --- | --- |
| `assets/_shared/series-featured.svg` | Default featured image (1200×630); no likeness |
| `assets/_shared/type-plate-essay.svg` | In-article type plate for ops / living-subject essays |
| `assets/_shared/portrait-pending.svg` | Rights not cleared (`confirm` rows) |

## Timelines and maps (original)

| ID | File | Embed in draft(s) | Alt summary |
| --- | --- | --- | --- |
| Fig. 01 | `graphics/fig-01-document-milestones.svg` | 05, 33, 43 | Publication and program dates 1979–2009 |
| Fig. 02 | `graphics/fig-02-clinic-places-map.svg` | 08, 25 | Worcester, Barre, Reno, London, Almería (schematic) |
| Fig. 03 | `graphics/fig-03-act-naming-dates.svg` | 17, 18, 22 | ACT naming chain 1980s–2005 |

## Per-essay featured image (YAML `featured_image`)

All forty-five drafts carry `meta_description` and `featured_image` (relative from essay file). See `tools/graphics_manifest.toml` for the machine list.

## QA

```bash
python3 content/act-mindfulness-therapy-history/tools/lint_claims.py
python3 content/act-mindfulness-therapy-history/tools/check_graphics.py
```
