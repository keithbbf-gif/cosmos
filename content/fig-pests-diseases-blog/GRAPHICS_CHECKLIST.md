# Graphics checklist — pests & diseases pack

**Drafts with `<figure>` + SEO alt/figcaption:** run `python tools/embed_fig_pack_figures.py pests` after rasters land.

**Rasters downloaded:** see `assets/images/_download_meta.json` and `RIGHTS.md`.

## Pipeline

1. `python tools/fig_pack_rasters.py pests`
2. `python tools/embed_fig_pack_figures.py pests`
3. Human: replace PD fills with `D:\FIGS` stills per `PHOTO_NOTES.md` before publish.

## Per-pillar PD pool

| Pillar | Shared assets | D:\FIGS folders to shoot first |
|--------|---------------|--------------------------------|
| nematodes | `shared/nematodes/*` | `Damaged Cuttings`, `Greenhouse photos`, `Figs` |
| rust | `shared/rust/*` | `Figs-summer-23`, `Figs`, `More Fig Pictures` |
| mosaic | `shared/mosaic/*` | `More Fig Pictures`, `Figs-summer-23` |
| beetles | `shared/beetles/*`, fruit reference | `Fig Fruit` |
| birds / wildlife | fruit reference | `Fig Fruit`, `Malta_Black_Fig` |
| diagnosis | mites, ants, armillaria, fruit | `Fig Fruit`, `Greenhouse photos` |
| biosecurity | fruit flies | extension stills if BFF arrives in AR |
| cultural / calendar | rust + fruit reference | same as rust + harvest |

Target: **45/45** drafts carry at least one `<figure>` block in git (PD staging) plus an `orchard_slot` HTML comment pointing at the `folder_pick` in front matter.
