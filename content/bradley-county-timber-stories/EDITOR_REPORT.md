# Editor report — Bradley County Timber Stories

**Pass date:** 2026-09-14  
**Base:** `cursor/bradley-county-timber-stories-0a31` (PR #318)  
**Branch:** `cursor/bradley-county-timber-editor-060b`  
**Editor:** Cloud agent (EDITOR role)

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed | 44 |
| Drafts with body edits | 32 |
| Drafts updated (`voice_check: edited`) | 44 |
| Hard-ban phrase hits (post-pass) | 0 |
| Commerce CTAs (`shop now`, `our craftsmen`, visit/sell invites) | 0 |

## What was fixed

1. **Ken Burns voice / fourth wall** — Removed or rewrote reader-coaching closings (`If you want a still…`, `If you stand…`, `Resist it`, `Do not go there`) in 29 drafts. Replaced series/essay meta (`This series will not…`, `This essay stops…`) with third-person, pack-bound phrasing where it broke the documentary tone.
2. **Grammar / spelling** — `courtsquare` → **court square** (`the-clock-at-waynes`). Sources: `Associated pressers` → **Associated Press** (`a-physician-buys-a-mill`).
3. **Commerce lane** — Confirmed `commerce: false` on all drafts; BBF / Bradley Brand Furniture remains heritage-only (no product names, no visit CTAs). Trimmed disclaimer stacking in `the-long-afterlife.md` while keeping the afterlife essay’s civic BBF bridge.
4. **Front matter** — All pack markdown: `voice_check: edited`, `voice_check_date: 2026-09-14`. Updated `INDEX.md`, `MANIFEST.md`, and `STYLE_GUIDE.md` example YAML to match.
5. **Unchanged on purpose** — `[CITE NEEDED]` markers, word counts, slugs, `writer-slugs.json`, reading order, Sources sections, and historical commerce language (scrip, mixed cars, wartime ads) as primary-source context.

## Files with substantive body edits

`a-physician-buys-a-mill`, `arkansas-lumber-cuts-out`, `august-fifth-eighteen-eighty`, `brick-streets-1927`, `commissary-and-scrip`, `court-at-the-captains-house`, `depression-lumber-banks-held`, `dry-kilns-and-the-smell`, `flooring-stock-and-furniture`, `good-friday-1975`, `joe-reaves-buys-timber`, `mill-town-america`, `names-on-the-time-clock`, `northern-money-southern-trees`, `one-hundred-thousand-board-feet`, `peninsula-between-the-rivers`, `photographs-and-letters`, `pink-tomato-and-pine`, `potlatch-years`, `rebuilding-the-stack`, `shortleaf-pine-country`, `the-clock-at-waynes`, `the-fullerton-sons`, `the-long-afterlife`, `three-mills-one-town`, `two-names-for-warren`, `warner-and-second-growth`, `wartime-lumber`, `when-the-hardwood-mill-closed`, `ymca-nineteen-twenty`.

## Clean after pass (no body edits beyond `voice_check`)

`after-the-big-mill`, `before-the-rail-the-small-mills`, `catfish-row`, `hardwood-and-pine`, `hermitage-banks-johnsville`, `hugh-bradley-comes-up-the-red`, `mill-housing-company-street`, `sunday-in-a-mill-town`, `the-filer`, `the-mill-whistle`, `the-sawyers-chair`, `warren-and-ouachita-valley`, `what-remains`, `women-in-slacks-1918`.

## Remaining weak spots

- **`mill-town-america.md`** — Capstone still carries a deliberate date roll call; it is framed as anti-brochure, but it is the longest list in the pack. A future writer pass could compress without losing the type-vs-particular argument.
- **Meta “this series”** — A few essays still use “this series” when describing source limits (`wartime-lumber`, `potlatch-years`, `hardwood-and-pine`). Acceptable as pack-bound honesty; not shop tone.
- **Gaps** — All `[CITE NEEDED]` items from the writer pass remain visible for a research pass.

## Not in scope

- No WordPress / WXR publish.
- No graphics or `assets/` additions.
- No merge (draft PR only).
