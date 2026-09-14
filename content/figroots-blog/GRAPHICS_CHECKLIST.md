# FigRoots graphics checklist (40+ pack)

**Current drafts with graphics:** 12 / 40+ target

Re-run `python content/figroots-blog/scripts/graphics_pipeline.py --all` when new drafts land.

## Shipped in this pass

- [x] `birds-pests-green-vs-dark-figs` — specs in `scripts/figroots_graphics/specs.py`
- [x] `breba-vs-main-crop-planning` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-cutting-rooting-failures` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-flavor-families` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-growing-degree-days` — specs in `scripts/figroots_graphics/specs.py`
- [x] `fig-soil-drainage-clay-beds` — specs in `scripts/figroots_graphics/specs.py`
- [x] `pot-vs-in-ground-figs-south` — specs in `scripts/figroots_graphics/specs.py`
- [x] `seasonal-fig-cuttings-calendar` — specs in `scripts/figroots_graphics/specs.py`
- [x] `storing-dormant-fig-cuttings` — specs in `scripts/figroots_graphics/specs.py`
- [x] `summer-shade-water-hot-south` — specs in `scripts/figroots_graphics/specs.py`
- [x] `tight-eye-vs-open-eye-humid-climates` — specs in `scripts/figroots_graphics/specs.py`
- [x] `verifying-fig-variety-true-to-type` — specs in `scripts/figroots_graphics/specs.py`

## Placeholder slugs (no draft file yet)

- [ ] #13 `fig-winter-dieback-arkansas` (climate) — pending draft
- [ ] #14 `caprifig-wasp-not-needed-common` (identity) — pending draft
- [ ] #15 `fig-pop-moisture-hand-test` (propagation) — pending draft
- [ ] #16 `thermostat-heat-mat-setup` (propagation) — pending draft
- [ ] #17 `variety-trial-row-layout` (culture) — pending draft
- [ ] #18 `fertigation-pots-south` (culture) — pending draft
- [ ] #19 `split-fruit-after-rain` (fruit) — pending draft
- [ ] #20 `netting-vs-harvest-timing` (fruit) — pending draft
- [ ] #21 `coir-de-ab-cite-not-repeat` (propagation) — pending draft
- [ ] #22 `field-capacity-promix` (culture) — pending draft
- [ ] #23 `zone-push-microclimate` (climate) — pending draft
- [ ] #24 `marketplace-cutting-red-flags` (propagation) — pending draft
- [ ] #25 `labeling-fig-tags` (identity) — pending draft
- [ ] #26 `bulk-start-shade-water` (propagation) — pending draft
- [ ] #27 `prune-timing-south` (culture) — pending draft
- [ ] #28 `fig-ripeness-pinch-test` (fruit) — pending draft
- [ ] #29 `ant-rain-sap-notes` (fruit) — pending draft
- [ ] #30 `container-size-up-calendar` (culture) — pending draft

## When a new draft appears

1. Add `FigureSpec` entries to `scripts/figroots_graphics/specs.py` (or a generator).
2. Run `graphics_pipeline.py --slug <slug>`.
3. Confirm `figures:` in front matter and embed markers `<!-- figroots-graphic: ... -->`.
