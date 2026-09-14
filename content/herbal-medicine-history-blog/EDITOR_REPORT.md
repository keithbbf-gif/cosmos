# EDITOR_REPORT — herbal medicine history blog

**Pass:** EDITOR (grammar, spelling, voice, claims guardrails)  
**Date:** 2026-09-14 (UTC)  
**Base reviewed:** `cursor/herbal-medicine-history-blog-231e` @ `52606eb` (WRITER pack; PR #255)  
**Editor branch:** `cursor/herbal-medicine-history-editor-7882`  
**Graphics upstream:** PR #242 (`cursor/herbal-medicine-history-graphics-594f`) — SVG `<figure>` embeds not on WRITER branch; this pass preserved all `> **Photo:**` / caption / license blocks unchanged.

## Verdict: **EDIT COMPLETE — prose pass landed**

All 45 drafts in `drafts/` carry **real body prose** (PACK QA word floor 650; observed range ~704–862 words). No stub hold.

| Metric | Count |
|--------|------:|
| Drafts scanned | 45 |
| Stub-only (awaiting WRITER) | **0** |
| Drafts copyedited this pass | **45** |
| `voice_check` set to `edited` | **45** |
| Photo slots altered | **0** |
| Claims guardrail violations found | **0** |
| STYLE_GUIDE banned furniture in body | **0** |

**Mean word count (body, post-edit):** ~749

## Copy changes (line-level)

| File | Change |
|------|--------|
| `17-kampo-japan.md` | `palpatation` → `palpation` |
| `27-pure-food-1906.md` | `discloseable` → `disclosable` |
| `22-withering-foxglove.md` | `drop-sy` → `dropsy` (matches *Dropsy* in Withering title) |
| `32-rauwolfia-reserpine.md` | Subject–verb: *isolation … and Serpasil* **are** the kind of … |
| `36-ergot-sandoz.md` | Removed misplaced Hoffmann/aspirin (Bayer/Elberfeld); Basel tied to Sandoz ergot/LSD line |
| `20-garcia-de-orta.md` | Cut duplicate Clusius/Latinization paragraph (already in prior section) |
| `02-mesopotamian-clay-recipes.md` | US spelling: `cataloged` |
| `16-african-pharmacopeias.md` | US spelling: `cataloged` |
| `19-physic-gardens.md` | US spelling: `unlabeled` |

No other mechanical errors required intervention. Proper names retained (Wight, Bein, Furst, Müller, etc.). Pharmacologic *trough*, book-*treats*, and DSHEA example strings left as written.

## Claims & voice review

- Full read against `CLAIMS_GUARDRAILS.md`: no present-tense product cure/prevent/treat claims; no reader dosing; no synthesis/how-to on controlled substances; folklore vs trial vs regulator kept separable.
- `STYLE_GUIDE.md` banned furniture scan: clean.
- Educational closers (e.g. Ötzi, sacraments, St. John's wort) retained; not expanded with new clinical claims.

## QA tooling

- `qa/check_pack.py` now accepts `voice_check: human` or `voice_check: edited`.
- `STYLE_GUIDE.md` documents the `edited` state after EDITOR.

## Articles completed (`voice_check: edited`)

All slugs in `INDEX.md` (01–45): `otzi-birch-polypore` through `scheduled-sacraments`.

## Dependencies & merge order

| Upstream | Status |
|----------|--------|
| WRITER (PR #255 / `cursor/herbal-medicine-history-blog-231e`) | **Prose landed** — base for this PR |
| Graphics (PR #242) | **Open** — merge after or with WRITER; re-run EDITOR only if figure blocks replace photo slots |
| EDITOR (this branch) | **Stack on WRITER** — grammar/voice/`voice_check` only |

Suggested order: merge #255 → merge #242 (figures) → merge this EDITOR PR (or merge EDITOR on top of WRITER before graphics if CMS imports prose first).

## Re-run triggers

Re-open EDITOR if WRITER replaces ledes, if graphics PR changes caption text inside `> **Photo:**` blocks, or if any draft drops below the 650-word stub floor.
