# IMAGE_SOURCES — nursery / wholesale cuttings (buyfigs)

Art-desk notes for the staged trade-education set. **Cleared rasters live in `assets/images/` with `RIGHTS.md`.** `D:\FIGS` field notes were not mounted in the cloud agent; sources below are USDA NAL pomological watercolors on Wikimedia Commons, USDA ARS zone map, Wellcome Collection, Encyclopaedia Britannica 1911, and CC-licensed *Ficus carica* garden photos.

House rules:

- Only *Ficus carica* (common fig) or USDA-documented cultivar plates — no decorative fake fruit.
- **No AI-generated** bench, box, label, or shipping imagery.
- Stock “happy mailer” photos are often wrong species; prefer honest plates with captions that say what the image is **not** (not Jack’s taped carton).
- USPS / state compliance is **[VERIFY]** in copy; images are not legal documents.
- Recheck every Commons license at import time.

## Shared library (reuse across drafts)

| Asset | Use | Commons / source |
| --- | --- | --- |
| `assets/images/propagation/usda-pom-cutting.jpg` | Take, pack, hold, land — dormant stick trade | [POM00001042](https://commons.wikimedia.org/wiki/File:Pomological_Watercolor_POM00001042.jpg) |
| `assets/images/shared/usda-phzm-2012.jpg` | Cooler temps, weather ship holds, season wall | [2012 USDA PHZM](https://commons.wikimedia.org/wiki/File:2012_USDA_Plant_Hardiness_Zone_Map_(USA).jpg) |
| `assets/images/botanical/wellcome-v0044761.jpg` | Moisture, liners, tags, stem anatomy | [Wellcome V0044761](https://commons.wikimedia.org/wiki/File:A_fig_plant_(Ficus_carica);_fruiting_stem_and_halved_fruit._Wellcome_V0044761.jpg) |
| `assets/images/living/amwell-fig-tree.jpg` | Mothers, blocks, porch land | [Amwell Fig (1)](https://commons.wikimedia.org/wiki/File:Amwell_Fig_(1).jpg) CC BY-SA 4.0 |
| `assets/images/living/hortus-leiden-fig-2021.jpg` | Pots vs field, greenhouse context | [Hortus Leiden 2021](https://commons.wikimedia.org/wiki/File:20210731_Hortus_botanicus_Leiden_-_Ficus_carica.jpg) |

## Cultivar plates (USDA NAL — public domain)

Used for **identity and grade language**, not as proof of bundle contents: Celeste `POM00007441`, Magnolia `POM00001043`, Calimyrna `POM00007440`, Nameless `POM00001044`, Royal Black `POM00001045`, Toulousienne `POM00001168`.

## Per-draft embed

Each `drafts/dNN-*.md` carries one `<figure>` with `figure-id` registered in `GRAPHICS_INDEX.md`. Run:

`python3 tools/fig_nursery_wholesale_graphics.py all`

after changing the registry in `tools/fig_nursery_wholesale_graphics.py`.
