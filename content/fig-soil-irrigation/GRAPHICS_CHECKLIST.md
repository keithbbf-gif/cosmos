# Graphics checklist — soil & irrigation pack

**Target:** 48/48 drafts carry at least one `<figure>` with SEO `alt` + `<figcaption>` in git (PD staging) plus an `orchard_slot` comment aimed at `D:\FIGS`.

## Pipeline

1. `python tools/fig_pack_rasters.py soil`
2. `python tools/embed_fig_soil_irrigation.py`
3. `python content/fig-soil-irrigation/validate.py`
4. Human: replace PD fills with `D:\FIGS` stills per `PHOTO_NOTES.md` before publish.

## Shared raster pools

| Stage | Shared assets | `D:\FIGS` folders to shoot first |
| --- | --- | --- |
| read (soil) | `shared/soil/*` | `Figs`, `Figs-summer-23` |
| fix (drainage) | `shared/drainage/*`, `shared/reference/*` | `Figs`, `Greenhouse photos` |
| cover (mulch) | `shared/mulch/*`, `shared/trouble/fig-rust*` | `Figs`, `Figs-summer-23` |
| water | `shared/irrigation/*` | `Greenhouse photos`, `Figs` |
| pot (media) | `shared/media/*`, `shared/drainage/potting-soil*` | `Greenhouse photos` |

Checksums: `assets/images/_download_meta.json`. Licences: `RIGHTS.md`.
