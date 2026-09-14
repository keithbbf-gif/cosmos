# Cherry-pick report — rights overlay (PR #275)

**Date:** 14 September 2026  
**Source:** `cursor/rights-hunt-portraits-0984` (GitHub PR #275)  
**Target branch:** `cursor/rights-overlay-cherry-pick-f1f8`  
**Method:** Writer-pack trees + rights-hunt ledgers/rasters + selective graphics banner updates.

## Packs merged

| Pack | Writer base | Overlay from #275 | Graphics merged |
|------|-------------|-------------------|-----------------|
| `content/ai-history-retrospective/` | `cursor/ai-history-retrospective-7b08` | `PORTRAIT_SOURCES.md`, `assets/retired/`, portraits (unchanged bytes) | `cursor/ai-history-graphics-aae1` portrait plates |
| `content/slpwow-speech-pathology-history/` | `cursor/slpwow-speech-pathology-history-b9a7` | `PORTRAIT_SOURCES.md`, placeholders, Visible Speech chart | Pending plates for Van Riper / Travis / Johnson |
| `content/wowtherapies-therapy-history/` | `cursor/wowtherapies-therapy-history-b51d` | `PORTRAIT_SOURCES.md`, `assets/portraits/`, `pipeline/portrait_sources.yaml` | `cursor/wowtherapies-therapy-history-graphics-9a7f` staged SVGs |
| `content/fig-history-ancient-to-today/` | `cursor/fig-history-ancient-to-today-771e` | `IMAGE_SOURCES.md`, `assets/images/` (19 rasters) | — (no pending raster banners on graphics branch) |

Shared tooling: `content/RIGHTS_HUNT_REPORT.md`, `RIGHTS_HUNT_REPORT.md`, `content/rights-hunt/verify_assets.py` (skip `_superseded/` crumbs like `retired/`).

## Pending banners dropped (`Status = cleared` only)

| Asset | Change |
|-------|--------|
| `ai-history-retrospective/assets/figure-marvin-minsky/portrait-plate.svg` | Embedded `../portraits/marvin-minsky.jpg`; removed hatch / “rights not cleared” / credit pending |
| `wowtherapies-therapy-history/staged/graphics/fig-03-portrait-plate-freud.svg` | Embedded `../../assets/portraits/sigmund-freud.jpg`; removed monogram pending-publish slot |

## Pending banners kept (honest)

| Asset | Why |
|-------|-----|
| `figure-alan-turing/portrait-plate.svg` | `caution` in ledger |
| `figure-john-mccarthy/portrait-plate.svg` | `caution` |
| `fig-04-portrait-plate-rogers.svg`, `fig-06-portrait-plate-ellis.svg` | `placeholder` |
| `fig-05-portrait-plate-beck.svg` | `caution` (1942 yearbook; pending-publish copy retained) |
| SLP `portrait-plate-pending.svg` (Van Riper, Travis, Johnson) | `placeholder` |
| All `*.placeholder.svg` under `assets/portraits/` | Not photographs |

## Writer-only retention

- **SLPWOW:** Essay-illustration portraits (Gall, Itard, Bouillaud, Lichtheim, Jackson, Head, Sicard) kept on disk; appendix table appended to `PORTRAIT_SOURCES.md`.
- **AI history:** Full retrospective prose, bibliography, and graphics SVGs from writer branch unchanged except Minsky plate.
- **Fig:** Prior `IMAGE_SOURCES.md` URL index superseded by hunt ledger for downloaded rasters; articles unchanged.

## Verification

```text
$ python3 content/rights-hunt/verify_assets.py
ledgers_rows=105 rasters=82 placeholders=22
OK every raster and placeholder is in a source ledger
```

## Not done here

- No generative faces invented.
- No ASHA omeka scraping.
- No live CMS / WordPress import.
