# FigRoots graphics checklist (40-draft pack)

**Current drafts with graphics:** 45 / 45

Re-run `python content/figroots-blog/scripts/graphics_pipeline.py --all` when headings or specs change.

Existing 1–12 asset paths stay under `assets/<slug>/`. New slugs add figures beside them.

## Shipped

- [x] `air-layer-vs-fig-cutting` — specs in `scripts/figroots_graphics/specs.py`
- [x] `arkansas-winter-protection-figs` — specs in `scripts/figroots_graphics/specs.py`
- [x] `birds-pests-green-vs-dark-figs` — specs in `scripts/figroots_graphics/specs.py`
- [x] `breba-vs-main-crop-planning` — specs in `scripts/figroots_graphics/specs.py`
- [x] `celeste-vs-brown-turkey-arkansas` — specs in `scripts/figroots_graphics/specs.py`
- [x] `collecting-figs-vs-eating-figs` — specs in `scripts/figroots_graphics/specs.py`
- [x] `common-figs-only-arkansas` — specs in `scripts/figroots_graphics/specs.py`
- [x] `daily-picking-fig-harvest-window` — specs in `scripts/figroots_graphics/specs.py`
- [x] `east-wall-fig-microclimate` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-cutting-rooting-failures` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-fall-harden-off-arkansas` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-fertigation-after-pot-up` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-flavor-families` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-freeze-recovery-multi-trunk` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-growing-degree-days` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-potting-mix-that-drains` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-rust-in-humidity` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-soil-drainage-clay-beds` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-split-vs-sour-after-rain` — specs in `scripts/figroots_graphics/specs.py`
- [x] `first-two-summers-in-ground-fig` — specs in `scripts/figroots_graphics/specs.py`
- [x] `grafting-over-a-dud-fig` — specs in `scripts/figroots_graphics/specs.py`
- [x] `heat-mat-thermostat-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `how-to-read-a-fig-cutting` — specs in `scripts/figroots_graphics/specs.py`
- [x] `inspecting-mail-order-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `labeling-fig-cuttings-and-pots` — specs in `scripts/figroots_graphics/specs.py`
- [x] `late-freeze-after-fig-budbreak` — specs in `scripts/figroots_graphics/specs.py`
- [x] `lsu-figs-for-humid-south` — specs in `scripts/figroots_graphics/specs.py`
- [x] `marketplace-fig-cutting-red-flags` — specs in `scripts/figroots_graphics/specs.py`
- [x] `outdoor-bulk-fig-starts` — specs in `scripts/figroots_graphics/specs.py`
- [x] `pot-up-fig-before-june` — specs in `scripts/figroots_graphics/specs.py`
- [x] `pot-vs-in-ground-figs-south` — specs in `scripts/figroots_graphics/specs.py`
- [x] `pruning-figs-for-cuttings-vs-fruit` — specs in `scripts/figroots_graphics/specs.py`
- [x] `root-knot-nematodes-fig-pots` — specs in `scripts/figroots_graphics/specs.py`
- [x] `seasonal-fig-cuttings-calendar` — specs in `scripts/figroots_graphics/specs.py`
- [x] `storing-dormant-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `summer-shade-water-hot-south` — specs in `scripts/figroots_graphics/specs.py`
- [x] `the-fig-shuffle-pots` — specs in `scripts/figroots_graphics/specs.py`
- [x] `tight-eye-vs-open-eye-humid-climates` — specs in `scripts/figroots_graphics/specs.py`
- [x] `unknown-figs-honest-names` — specs in `scripts/figroots_graphics/specs.py`
- [x] `variety-trial-row-figs` — specs in `scripts/figroots_graphics/specs.py`
- [x] `verifying-fig-variety-true-to-type` — specs in `scripts/figroots_graphics/specs.py`
- [x] `water-rooting-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `when-to-pot-up-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `why-figs-drop-fruit` — specs in `scripts/figroots_graphics/specs.py`
- [x] `winter-shop-scale-figs` — specs in `scripts/figroots_graphics/specs.py`

## Drafts still missing specs

- none

## When a new draft appears

1. Add `FigureSpec` entries to `scripts/figroots_graphics/specs.py` (or a generator).
2. Run `graphics_pipeline.py --slug <slug>`.
3. Confirm `figures:` in front matter and embed markers `<!-- figroots-graphic: ... -->`.
4. Keep existing `../assets/<slug>/<file_id>.svg` paths if the slug already shipped.
