# Graphics checklist — variety profiles pack

**Target:** 46/46 drafts with `<figure>` + SEO `alt` / `<figcaption>`.

## Pipeline

1. `python tools/fig_pack_rasters.py varieties`
2. `python tools/embed_fig_pack_figures.py varieties`
3. Replace USDA/botanical fills with `D:\FIGS` stills per `PHOTO_NOTES.md` before publish.

## Status

- [x] USDA NAL pomological plates downloaded (`assets/images/cultivars/`)
- [x] Generic botanical references (`assets/images/shared/reference/`)
- [x] All 46 drafts embed `<figure>` blocks with `orchard_slot` comments
- [ ] Keith stills for LSU releases, Panache stripes, Malta Black, Maryland Berry, I-258, Yellow Long Neck
