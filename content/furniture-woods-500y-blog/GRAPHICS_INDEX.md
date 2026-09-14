# GRAPHICS_INDEX — furniture-woods-500y-blog

**Quality bar:** five publish-ready figures, magazine typography, no decorative chrome. Numeric labels cite USDA FPL *Wood Handbook* / Wood Database; CITES notes cite cites.org.

Writer draft slugs are canonical in `writer-slugs.json` (46 slugs). **Pre-built embed blocks** for each slug live in `staged-embeds/<slug>.md` — copy into `drafts/<slug>.md` when the writer merges text.

## Figure set (5 SVGs)

| Fig | Asset path | Use |
|-----|------------|-----|
| 1 | `assets/timber-trade-500y/timeline.svg` | Global 1540–2030 milestones |
| 2 | `assets/timber-trade-500y/trade-lanes.svg` | Baltic oak / mahogany / teak lanes |
| 3 | `assets/grain-cuts/sawn-orientation.svg` | Flatsawn, quartersawn, rift |
| 4 | `assets/species-comparison/core-species-properties.svg` | Janka × density scatter (10 species) |
| 5 | `assets/cites-conservation/furniture-timber-listings.svg` | CITES appendix schematic |

## Embed workflow

From a draft at `drafts/mahogany-chippendale.md`, include:

```markdown
<!-- from staged-embeds/mahogany-chippendale.md -->
```

Or reference figures directly:

```markdown
![Three trade lanes](../assets/timber-trade-500y/trade-lanes.svg)

*Figure 2. Three parallel supply chains — Baltic oak, Atlantic mahogany, and Indian Ocean teak — with documentary milestone years.*
```

Paths are relative from `drafts/` (one level up to `assets/`).

## Slug → figures

| Draft slug | Figures |
|------------|---------|
| `intro-500-year-timber` | 1, 4 |
| `glossary-grain-and-cut` | 3 |
| `baltic-oak-renaissance` | 2, 4 |
| `english-oak-great-furniture` | 4, 3 |
| `dutch-golden-age-shipping` | 2, 1 |
| `navy-oak-reserves` | 2, 1 |
| `american-colonial-pine` | 4, 1 |
| `white-pine-softwood-economy` | 4 |
| `walnut-baroque` | 4, 3 |
| `walnut-queen-anne` | 4, 3 |
| `mahogany-chippendale` | 2, 4 |
| `mahogany-federal-america` | 2, 4 |
| `mahogany-regency-empire` | 2, 5 |
| `rosewood-victorian` | 4, 3 |
| `rosewood-gothic-revival` | 4, 5 |
| `teak-colonial-dockyards` | 2, 4 |
| `teak-deck-and-garden` | 4, 2 |
| `ebony-inlay-keys` | 4, 5 |
| `maple-birdseye-factory` | 4, 3 |
| `cherry-shaker` | 4 |
| `yew-medieval-turnery` | 4 |
| `satinwood-adam-style` | 4, 3 |
| `beech-bentwood-thonet` | 4 |
| `ash-sporting-chairs` | 4 |
| `cedar-lining-chests` | 4 |
| `boxwood-inlay` | 4 |
| `padauk-modernist-accents` | 4, 5 |
| `cites-1973-convention` | 5, 1 |
| `cites-dalbergia-2017` | 5, 4 |
| `cites-swietenia-permits` | 5, 2 |
| `cites-ebony-africa` | 5, 4 |
| `sustainable-teak-plantations` | 2, 5 |
| `reclaimed-oak-beams` | 4, 1 |
| `quartersawn-arts-crafts` | 3, 4 |
| `flatsawn-panel-figure` | 3 |
| `rift-cut-flooring` | 3 |
| `moisture-wood-movement` | 3, 4 |
| `janka-hardness-explained` | 4 |
| `density-weight-shipping` | 4, 1 |
| `workability-hand-tools` | 4, 3 |
| `veneer-versus-solid` | 3, 4 |
| `brazilian-rosewood-midcentury` | 4, 5 |
| `indian-rosewood-exports` | 4, 1 |
| `plywood-and-core-stock` | 3, 1 |
| `tropical-hardwood-peak-1900` | 1, 4 |
| `conservation-today` | 5, 1 |

Full copy-paste blocks: `staged-embeds/<slug>.md`.

## Sources (figure notes)

| Data | Reference |
|------|-----------|
| Janka & density | USDA Forest Products Laboratory, *Wood Handbook*; wood-database.com species means |
| Cut geometry | R. B. Hoadley, *Understanding Wood* (Taunton) |
| CITES listings | [cites.org](https://cites.org) — re-verify at publication |
| Trade years | Per-draft bibliography; lane milestones are order-of-magnitude |

## Regeneration

```bash
python3 content/furniture-woods-500y-blog/_staging/build_graphics.py
```

Removes legacy per-species asset folders automatically.
