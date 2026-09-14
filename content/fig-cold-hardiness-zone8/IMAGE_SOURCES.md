# IMAGE_SOURCES — fig cold hardiness (Zone 8a focus)

Art-desk notes for the staged winter set. **Cleared rasters live in `assets/images/` with `RIGHTS.md`.** User `D:\FIGS` field notes were not mounted in the cloud agent; sources below are USDA ARS / extension context, USDA NAL pomological watercolors on Wikimedia Commons, Wellcome Collection, and CC-licensed *Ficus carica* garden photos.

House rules:

- Only *Ficus carica* (common fig) or USDA-documented cultivar plates — no decorative fake fruit, no *Ficus sycomorus* unless labeled.
- Winter-wrap stock photos are often wrong species or Mediterranean villa clichés; prefer honest living-tree and USDA voucher plates with captions that say what the image is **not** (not your wrapped tree).
- Recheck every Commons license at import time.

## Shared library (reuse across drafts)

| Asset | Use | Commons / source |
| --- | --- | --- |
| `assets/images/shared/usda-phzm-2012.jpg` | Zone math, 8a/8b, vortex context | [2012 USDA PHZM (USA)](https://commons.wikimedia.org/wiki/File:2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg) |
| `assets/images/botanical/wellcome-v0044761.jpg` | Wood/fruit anatomy, drought-freeze | [Wellcome V0044761](https://commons.wikimedia.org/wiki/File:A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg) |
| `assets/images/living/amwell-fig-tree.jpg` | Yard tree, wrap timing, dieback | [Amwell Fig (1)](https://commons.wikimedia.org/wiki/File:Amwell_Fig_(1).jpg) CC BY-SA 4.0 |
| `assets/images/living/hortus-leiden-fig-2021.jpg` | Canopy, Zone 9 restraint, patio | [Hortus Leiden 2021](https://commons.wikimedia.org/wiki/File:20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg) |

## Variety plates (USDA NAL — public domain)

Celeste `POM00007441`, Magnolia `POM00001043`, Calimyrna 1912 `POM00007440`, cutting wood `POM00001042`, Toulousienne `POM00001168`, caprifig Endgere `POM00001071`, plus nameless and Royal Black for catalog-hardy essays.

## Per-draft embed

Each `drafts/dNN-*.md` carries one `<figure>` with `figure-id` registered in `GRAPHICS_INDEX.md`. Run `python3 tools/fig_zone8_graphics.py all` after changing the registry.
