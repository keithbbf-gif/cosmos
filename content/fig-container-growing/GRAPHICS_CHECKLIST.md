# Graphics checklist — container growing pack

**Target:** 47/47 numbered drafts carry at least one `<figure>` with SEO `alt` + `<figcaption>` in git (PD staging) plus an `orchard_slot` comment aimed at `D:\FIGS`.

## Pipeline

1. `python tools/fig_pack_rasters.py container`
2. `python tools/embed_fig_container_growing.py`
3. `python content/fig-container-growing/validate.py`
4. Human: replace PD fills with `D:\FIGS` stills per `PHOTO_NOTES.md` before publish.

## Shared raster pools

| Topic lane | Shared assets | `D:\FIGS` folders to shoot first |
| --- | --- | --- |
| pots & media | `shared/media/*`, `shared/drainage/potting-soil*`, `shared/pots/*` | `Greenhouse photos` |
| water | `shared/irrigation/*` | `Greenhouse photos`, `Figs` |
| zones & calendar | `shared/reference/*`, `shared/weather/*` | `Figs`, `Figs-summer-23` |
| varieties (staging) | `cultivars/*`, `shared/reference/ehret-*` | `Fig Fruit` (hero), USDA plates as fill |
| trouble | `shared/trouble/*`, `shared/diagnosis/*`, `shared/nematodes/*` | `Figs-summer-23` |

Checksums: `assets/images/_download_meta.json`. Licences: `RIGHTS.md`.
