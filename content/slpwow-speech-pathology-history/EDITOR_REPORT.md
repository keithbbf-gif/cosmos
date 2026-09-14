# Editor report — SLPWOW speech-pathology history

**Pass date:** 2026-09-14  
**Branch:** `cursor/slpwow-speech-pathology-history-editor-eb6e` (stacked on `cursor/slpwow-speech-pathology-history-b9a7`, writer PR #254)  
**Editor:** Cloud agent (EDITOR role)  
**Graphics context:** #243 / graphics pipeline on the writer branch (SVG seed + portrait-pending plates)

## Verdict: proceed (not a stub pack)

| Check | Result |
|-------|--------|
| Articles in `articles/` | 40 |
| Stub / placeholder bodies | **0** — no shared boilerplate, no “coming soon,” no empty sections |
| Body word count range | ~469–1,018 words per file (~25.5k total) |
| Profiles under 550 words | 14 (allowed per `STYLE_GUIDE.md` when sentences earn their keep) |
| Hard-ban phrase hits (post-pass) | **0** |
| Synthetic / generated portrait likenesses | **0** — cleared files in `assets/portraits/` only; pending plates are labeled SVG placeholders |
| `<figure>` / portrait embeds touched | **0** structural changes |

**HOLD not issued.** The writer pack is full magazine copy with figures, credits, and explicit uncertainty where sources disagree.

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed (full read + scan) | 40 |
| Drafts updated (`voice_check: edited`) | 40 |
| Prose line edits in this pass | 2 |
| Pack metadata files updated | 4 (`INDEX.md`, `STYLE_GUIDE.md`, `WP_IMPORT.md`, this report) |

## What was fixed

1. **Front matter** — Replaced `voice_check: human` with `voice_check: edited` and added `voice_check_date: 2026-09-14` on every article.
2. **Ban list** — Scanned bodies for delve, landscape, leverage, robust, seamless, tapestry, unlock, empower, journey, holistic approach, “it is important to note,” “In today’s…,” “Whether you’re…”. No matches before or after the pass.
3. **Grammar / house style (targeted)**  
   - `articles/14-mayo-motor-speech.md` — “not under our hand” → “not in hand when this pack was staged” (consistent with other pack-level sourcing lines).  
   - `articles/15-from-correction-to-csd.md` — “school room” → “schoolroom” (American English).
4. **Preserved** — All portrait `<figure>` blocks, markdown `![…]` images, `figure-credit` spans, `portrait-plate-pending.svg` paths, `assets/portraits/*` references, and editorial SVG paths under `assets/`. No new likenesses; no AI faces.

## Voice notes (no rewrite required)

- Openings are scene- or object-led; corporate SLP brochure tone is absent.
- Meta lines (“this pack,” “this series will not…”) are intentional transparency for contested dates and missing obituaries — left in place per `STYLE_GUIDE.md` claims-and-caution rules.
- Difficult history (Milan, Johnson/Davenport, Broca’s anthropology, Bell’s 1883 memoir) is on the page without sermonizing.

## Remaining weak spots (for a later writer or photo pass)

| Area | Note |
|------|------|
| Portrait rights | Most profiles still use `portrait_status: placeholder` or pending SVG plates; hunt list in `PORTRAIT_SOURCES.md` unchanged. |
| Incomplete vitae | Brookshire, McDonald, and similar profiles correctly stop at citable facts; death dates may land later. |
| Length | Shortest profiles (~470 words) are tight but complete; era essays carry the long-form weight. |
| Graphics #243 | Seed SVGs are schematic teaching art, not clinical instruments — captions already say so. |

## Articles flagged for extra care (already honest in copy)

| Slug | Note |
|------|------|
| `wendell-johnson` | Monster Study and Davenport handled as ethics, not curiosity. |
| `alexander-graham-bell` | Oralism + 1883 memoir on same page as Visible Speech. |
| `paul-broca` | Craniometry named alongside the 1861 case. |
| `global-profession` | Admits non-U.S. histories need language-local writers. |

## Not in scope

- No changes to `assets/**/*.svg` (graphics branch remains source for diagrams).
- No WordPress publish actions.
- No COSMOS core / live tree paths.

## Verification commands (reproducible)

```bash
rg -c 'voice_check: edited' content/slpwow-speech-pathology-history/articles | wc -l   # expect 40
rg -i 'delve|landscape|leverage|robust|seamless|tapestry' content/slpwow-speech-pathology-history/articles || true
wc -w content/slpwow-speech-pathology-history/articles/*.md
```
