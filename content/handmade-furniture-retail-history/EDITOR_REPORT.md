# Editor report — handmade-furniture-retail-history

**Pass date:** 2026-09-14  
**Branch:** `cursor/handmade-furniture-retail-history-0c2a` (editor pass on staged BBF drafts from PR #304 / `cursor/handmade-furniture-retail-history-ec68`)  
**Editor:** Cloud agent (EDITOR role)

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed | 44 |
| Drafts updated (`voice_check: edited`) | 44 |
| Hard-ban phrase hits (post-pass) | 0 |
| `educational_claim` frontmatter | unchanged (44) |
| `validate_staging.py` | PASS |

## What was fixed

1. **Front matter** — Added `voice_check: edited` and `voice_check_date: 2026-09-14` on every draft in `drafts/`.
2. **Clarity / voice** — Removed or rewrote lines that broke the fourth wall or read like essay scaffolding (`07-44` staging note; stacked outline in `05-33`; meta lines in `05-30`, `06-35`, `06-41`, `07-42`).
3. **Narrator consistency** — Aligned opener in `00-01` with `00-02`: showroom/market experience vs watching platform pipes from the bench (no implied Overstock/Wayfair shop memoir).
4. **Grammar / usage** — `01-06` exposure line (checks → bankruptcies); US spelling `canceled` in `06-34`; `bombé` for the secretary piece in `00-02`; softened `05-29` impulse line (`reckless` vs `unwell`).
5. **“The educational point” closers** — Replaced eleven template closers with spoken equivalents (same claims, less worksheet tone) across `00-03`, `01-08`, `01-10`, `02-15`, `02-18`, `02-19`, `04-26`, `05-28`, `05-31`, `06-38`, `06-39`.
6. **Ban list** — Scanned bodies for `validate_staging.py` banned phrases and sales-close strings (`add to cart`, `use code`). No matches after the pass.
7. **Preserved** — All `educational_claim` YAML, series sequence, public-history dates and attributions (Etsy 2005/2013, Overstock/CSN/Wayfair mechanics, America House, ACC fairs, High Point). No invented Overstock/Wayfair contracts or shop-specific PO dollar figures were added.

## Remaining weak spots (for Keith’s on-camera cut)

- **Triad closers** — Many drafts still end with parallel “If you are a maker / buyer / designer” blocks. Intentional series rhythm; vary on mic where it feels cloned.
- **Motif density** — Shared images (four doors, “who owns the customer,” “hospital wing,” jewelry weather, seven-million-SKU rhetoric) repeat by design; a few episodes back-to-back may echo.
- **Fact-check before air** — Public claims flagged for host verification (unchanged by editor): Etsy fee/ad rate cards (explicitly stale-safe in copy), Etsy Wholesale product life, Wayfair S-1 magnitudes, `07-43` 2011 award wording, biographical shop stats in `00-02`.
- **06-36 opening** — Dropship-as-HR-bullet list is strong content; may need a breath on camera before the list lands.

## Articles that still risk a flat read (lower confidence)

| File | Note |
|------|------|
| `03-23-market-order-vs-cart.md` | Tight parallel prose; fine once VO slows. |
| `06-38-sku-flood.md` | Abstract catalog exercise; benefits from one concrete example on camera. |
| `07-44-series-close.md` | Deliberate recap stack; keep energy up through the door list. |

## Not in scope

- No changes outside `content/handmade-furniture-retail-history/`.
- No publish / WP / channel upload actions.
- `MANIFEST.json` word counts unchanged (editor pass did not materially shift length).
- No merge (draft PR only).
