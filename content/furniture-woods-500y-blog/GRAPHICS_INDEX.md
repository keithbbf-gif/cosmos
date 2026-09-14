# GRAPHICS_INDEX — furniture-woods-500y-blog

Staged SVG figures for the 500-year furniture timber series. Each asset includes an on-figure caption band with source notes where numeric data appear.

## Asset catalog

| Slug folder | File | Figure ID | Type |
|-------------|------|-----------|------|
| `timber-trade-500y` | `timeline-global.svg` | `fig-trade-500y-global` | 500-year trade timeline |
| `timber-trade-baltic-oak` | `trade-milestones.svg` | `fig-trade-baltic` | Regional trade timeline |
| `timber-trade-mahogany-atlantic` | `trade-milestones.svg` | `fig-trade-mahogany` | Regional trade timeline |
| `timber-trade-teak-asia` | `trade-milestones.svg` | `fig-trade-teak` | Regional trade timeline |
| `grain-cuts` | `quartersawn-flatsawn-rift.svg` | `fig-grain-cuts` | Quartersawn / flatsawn / rift |
| `grain-cuts` | `veneer-slicing-flitch.svg` | `fig-veneer-slice` | Veneer slicing schematic |
| `cites-conservation` | `regional-appendix-overview.svg` | `fig-cites-world` | CITES regional overview |
| `cites-conservation` | `swietenia-cites-detail.svg` | `fig-cites-swietenia` | Mahogany CITES detail |
| `cites-conservation` | `dalbergia-cites-detail.svg` | `fig-cites-dalbergia` | Dalbergia CITES detail |
| `species-comparison` | `janka-hardwoods.svg` | `fig-cmp-janka` | Species comparison (hardness) |
| `species-comparison` | `density-oven-dry.svg` | `fig-cmp-density` | Species comparison (density) |
| `species-comparison` | `dimensional-stability-ranking.svg` | `fig-cmp-stability` | Stability ranking |
| `species-comparison` | `workability-index.svg` | `fig-cmp-workability` | Workability index |
| `species-oak-european` | `species-profile.svg` | `fig-sp-oak-eu` | Species profile |
| `species-oak-white` | `species-profile.svg` | `fig-sp-oak-us` | Species profile |
| `species-mahogany-honduran` | `species-profile.svg` | `fig-sp-mahogany` | Species profile |
| `species-walnut-black` | `species-profile.svg` | `fig-sp-walnut` | Species profile |
| `species-teak` | `species-profile.svg` | `fig-sp-teak` | Species profile |
| `species-rosewood-indian` | `species-profile.svg` | `fig-sp-rw-in` | Species profile |
| `species-rosewood-brazilian` | `species-profile.svg` | `fig-sp-rw-br` | Species profile |
| `species-ebony-gabon` | `species-profile.svg` | `fig-sp-ebony` | Species profile |
| `species-maple-hard` | `species-profile.svg` | `fig-sp-maple` | Species profile |
| `species-cherry-black` | `species-profile.svg` | `fig-sp-cherry` | Species profile |
| `species-pine-eastern-white` | `species-profile.svg` | `fig-sp-pine` | Species profile |
| `species-yew` | `species-profile.svg` | `fig-sp-yew` | Species profile |
| `species-satinwood` | `species-profile.svg` | `fig-sp-satinwood` | Species profile |
| `species-beech` | `species-profile.svg` | `fig-sp-beech` | Species profile |
| `species-ash-white` | `species-profile.svg` | `fig-sp-ash` | Species profile |
| `species-cedar-atlas` | `species-profile.svg` | `fig-sp-cedar` | Species profile |
| `species-boxwood` | `species-profile.svg` | `fig-sp-boxwood` | Species profile |
| `species-padauk` | `species-profile.svg` | `fig-sp-padauk` | Species profile |

## Embed snippets (copy into drafts)

Paths assume the draft lives in `content/furniture-woods-500y-blog/drafts/<draft-slug>.md`.

### Global trade timeline

```markdown
![500-year furniture timber trade milestones](../assets/timber-trade-500y/timeline-global.svg)

*Figure: Selected milestones in Atlantic, Baltic, and tropical furniture-timber trade, 1520s–2020s. Policy dates follow CITES (cites.org).*
```

### Grain & cuts

```markdown
![Quartersawn, flatsawn, and riftsawn orientation](../assets/grain-cuts/quartersawn-flatsawn-rift.svg)

*Figure: Log orientation and typical face-grain results for flatsawn (tangential), quartersawn (radial), and riftsawn boards.*
```

```markdown
![Veneer slicing from a flitch](../assets/grain-cuts/veneer-slicing-flitch.svg)

*Figure: Sequential veneer leaves cut from a flitch; nominal thickness per HPVA/ANSI practice.*
```

### CITES & conservation

```markdown
![CITES regional overview for furniture timbers](../assets/cites-conservation/regional-appendix-overview.svg)

*Figure: Schematic regions with appendix notes for commonly traded furniture species (not a GIS range map).*
```

```markdown
![Swietenia CITES listing snapshot](../assets/cites-conservation/swietenia-cites-detail.svg)

*Figure: Appendix I/II status summary for true mahoganies (Swietenia spp.).*
```

```markdown
![Dalbergia Appendix II breadth](../assets/cites-conservation/dalbergia-cites-detail.svg)

*Figure: Post-2017 Dalbergia listing scope and documentation expectations for trade.*
```

### Species comparison charts

```markdown
![Janka hardness comparison](../assets/species-comparison/janka-hardwoods.svg)

*Figure: Side hardness (Janka, lbf) for historical furniture species — USDA FPL / Wood Database means.*
```

```markdown
![Oven-dry density comparison](../assets/species-comparison/density-oven-dry.svg)

*Figure: Mean oven-dry density (kg/m³) for the same species set.*
```

```markdown
![Dimensional stability ranking](../assets/species-comparison/dimensional-stability-ranking.svg)

*Figure: Qualitative indoor stability ranking (literature consensus; not site EMC).*
```

```markdown
![Workability index](../assets/species-comparison/workability-index.svg)

*Figure: Narrative workability scale for hand and machine processing.*
```

### Per-species profile template

Replace `<species-folder>` with a row from the catalog (e.g. `species-walnut-black`).

```markdown
![Species property profile](../assets/<species-folder>/species-profile.svg)

*Figure: Janka hardness and oven-dry density for the species discussed in this draft.*
```

## Draft → recommended figures (≥40 drafts)

| Draft slug | Primary figures |
|------------|-----------------|
| `intro-500-year-timber` | `fig-trade-500y-global`, `fig-cmp-janka` |
| `glossary-grain-and-cut` | `fig-grain-cuts`, `fig-veneer-slice` |
| `baltic-oak-renaissance` | `fig-trade-baltic`, `fig-sp-oak-eu` |
| `english-oak-great-furniture` | `fig-sp-oak-eu`, `fig-cmp-stability` |
| `dutch-golden-age-shipping` | `fig-trade-baltic`, `fig-trade-500y-global` |
| `navy-oak-reserves` | `fig-trade-baltic`, `fig-sp-oak-eu` |
| `american-colonial-pine` | `fig-sp-pine`, `fig-cmp-workability` |
| `white-pine-softwood-economy` | `fig-sp-pine`, `fig-cmp-density` |
| `walnut-baroque` | `fig-sp-walnut`, `fig-cmp-janka` |
| `walnut-queen-anne` | `fig-sp-walnut`, `fig-grain-cuts` |
| `mahogany-chippendale` | `fig-trade-mahogany`, `fig-sp-mahogany` |
| `mahogany-federal-america` | `fig-trade-mahogany`, `fig-cmp-workability` |
| `mahogany-regency-empire` | `fig-sp-mahogany`, `fig-cites-swietenia` |
| `rosewood-victorian` | `fig-sp-rw-in`, `fig-veneer-slice` |
| `rosewood-gothic-revival` | `fig-sp-rw-br`, `fig-cites-dalbergia` |
| `teak-colonial-dockyards` | `fig-trade-teak`, `fig-sp-teak` |
| `teak-deck-and-garden` | `fig-sp-teak`, `fig-cmp-stability` |
| `ebony-inlay-keys` | `fig-sp-ebony`, `fig-cites-world` |
| `maple-birdseye-factory` | `fig-sp-maple`, `fig-grain-cuts` |
| `cherry-shaker` | `fig-sp-cherry`, `fig-cmp-workability` |
| `yew-medieval-turnery` | `fig-sp-yew`, `fig-cmp-janka` |
| `satinwood-adam-style` | `fig-sp-satinwood`, `fig-veneer-slice` |
| `beech-bentwood-thonet` | `fig-sp-beech`, `fig-cmp-density` |
| `ash-sporting-chairs` | `fig-sp-ash`, `fig-cmp-janka` |
| `cedar-lining-chests` | `fig-sp-cedar`, `fig-cmp-stability` |
| `boxwood-inlay` | `fig-sp-boxwood`, `fig-cmp-janka` |
| `padauk-modernist-accents` | `fig-sp-padauk`, `fig-cites-dalbergia` |
| `cites-1973-convention` | `fig-cites-world`, `fig-trade-500y-global` |
| `cites-dalbergia-2017` | `fig-cites-dalbergia`, `fig-sp-rw-br` |
| `cites-swietenia-permits` | `fig-cites-swietenia`, `fig-sp-mahogany` |
| `cites-ebony-africa` | `fig-cites-world`, `fig-sp-ebony` |
| `sustainable-teak-plantations` | `fig-sp-teak`, `fig-trade-teak` |
| `reclaimed-oak-beams` | `fig-sp-oak-eu`, `fig-sp-oak-us` |
| `quartersawn-arts-crafts` | `fig-grain-cuts`, `fig-sp-oak-us` |
| `flatsawn-panel-figure` | `fig-grain-cuts`, `fig-sp-walnut` |
| `rift-cut-flooring` | `fig-grain-cuts`, `fig-sp-maple` |
| `moisture-wood-movement` | `fig-cmp-stability`, `fig-grain-cuts` |
| `janka-hardness-explained` | `fig-cmp-janka`, `fig-sp-ebony` |
| `density-weight-shipping` | `fig-cmp-density`, `fig-trade-500y-global` |
| `workability-hand-tools` | `fig-cmp-workability`, `fig-sp-pine` |
| `veneer-versus-solid` | `fig-veneer-slice`, `fig-grain-cuts` |
| `brazilian-rosewood-midcentury` | `fig-sp-rw-br`, `fig-cites-dalbergia` |
| `indian-rosewood-exports` | `fig-sp-rw-in`, `fig-trade-500y-global` |
| `plywood-and-core-stock` | `fig-veneer-slice`, `fig-sp-beech` |
| `tropical-hardwood-peak-1900` | `fig-trade-500y-global`, `fig-cmp-density` |
| `conservation-today` | `fig-cites-world`, `fig-cites-dalbergia`, `fig-cites-swietenia` |

## Source bibliography (figure notes)

| Topic | Primary references |
|-------|-------------------|
| Janka & density numbers | USDA Forest Products Laboratory, *Wood Handbook* (centroid species values); The Wood Database (wood-database.com) |
| CITES status | cites.org — Appendices & species checklists (verify at publication time) |
| Grain/cut geometry | R. B. Hoadley, *Understanding Wood* |
| Veneer thickness | ANSI/HPVA HP-1 (nominal thickness classes) |
| Trade milestone years | Draft-specific historiography; timeline figure marks widely cited order-of-magnitude dates |

## Regeneration

```bash
python3 content/furniture-woods-500y-blog/_staging/build_graphics.py
```
