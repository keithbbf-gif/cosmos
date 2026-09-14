# Editor report — herbal-medicine history pack (graphics #242 / PR #274 stack)

**Pass:** EDITOR (prose on graphics shells)  
**Branch stack:** `cursor/editor-herbal-history-6073` → `cursor/herbal-history-prose-on-graphics-231e`  
**Date:** 2026-09-14  
**Articles touched:** 40/40 in `articles/`  
**Front matter:** `voice_check: edited` on every file; `status: draft` unchanged; `graphics_agent: v1` unchanged.

## Figure contract (unchanged)

Automated diff against `origin/cursor/herbal-history-prose-on-graphics-231e` confirms for all 40 files:

- YAML `figures:` lists unchanged  
- First two `##` H2 headings unchanged  
- Both `<!-- graphics-pack:v1 -->` markers present  
- SVG `![...](../assets/...)` embed paths unchanged  
- `*Figure 1.*` / `*Figure 2.*` caption lines unchanged  

No new figures, no caption edits, no reordering.

## Prose work

| Category | Action |
|----------|--------|
| **Scaffolding removed** | Deleted `<!-- prose-expand:v1 … -->` tail sections (word-count padding that repeated closing sections) from 32 articles. Removed `<!-- under-fig:v2 -->` builder comments. |
| **Duplicate paragraphs** | Merged or cut repeated blocks after Figure 2 (or equivalent H2) in **04, 06, 07, 08, 09, 21, 26, 39** and tightened **03** (repeated corpus title list). |
| **Length floor** | Body word count (prose only): **min 700**, max 887, mean ~763 after dedupe. Articles **10, 17, 18, 22, 25, 31, 39** received short closing lines or `[VERIFY]` hooks where dedupe had dipped below 700. |
| **Voice** | Magazine-history tone retained; banned tokens scan clean (no delve/leverage/robust/seamless/tapestry/underscore/ever-evolving, etc.). |
| **Grammar / spelling** | Light line edit across the set; curly/straight quote normalization where duplicates were merged. |

## Claims guardrails

- No new therapeutic, dosing, or “use this plant to treat …” claims added.  
- Existing disclaimers and DSHEA / regulatory dull lines preserved.  
- `[VERIFY]` and **soft** plant-ID markers kept or added only for dating/sourcing discipline, not efficacy.  
- Aligns with `CLAIMS_GUARDRAILS.md`.

## QA tooling

- `qa/check_pack.py` now accepts `voice_check: human` **or** `voice_check: edited`.  
- Run: `python3 qa/check_pack.py` from `content/herbal-medicine-history-blog/`.  
- Note: default graphics ref `origin/cursor/herbal-medicine-history-graphics-594f` may be absent on a shallow clone; figure contract was verified against the prose branch as above.

## Articles with substantive dedupe (not exhaustive)

01–02, 05, 11–16, 20, 23–24, 27–30, 32–38, 40 — line edit + `voice_check` only unless noted in git diff.  
**Heavier merge:** 04, 06, 07, 08, 09, 10, 17, 18, 21, 22, 25, 26, 31, 39.

## Handoff

Ready for Keith publish review on the **graphics + prose** lane (#274). Not stacked on prose-only lanes #255 / #270.
