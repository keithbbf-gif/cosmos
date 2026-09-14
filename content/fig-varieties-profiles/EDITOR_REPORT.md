# Editor report — fig variety profiles

**Date:** 2026-09-14  
**Scope:** `content/fig-varieties-profiles/` (46 drafts + house files)  
**Upstream:** PR #319 (`cursor/fig-varieties-profiles-a8a6`)  
**Editor branch:** `cursor/fig-varieties-editor-c19e`  
**Gate:** `voice_check: edited` on all 46 drafts  

## Method

1. Read `STYLE_GUIDE.md` (PapaFig voice, ban list, front matter).
2. Full read of 18 representative drafts; skim of all 46 for ban-list terms, YAML, and paired-section duplication (“How I run it” / “How I would run it”).
3. Automated scan: STYLE_GUIDE ban list, repeated closing blocks, YAML colons in unquoted strings.
4. **Preserved on purpose:** Keith’s “not a fan of Brown Turkey / Celeste so far”; Jack’s Fig Jam ranking order; unofficial LSU (Hollier, Jack Lily); holding profiles (Yellow Long Neck, Italian 258); Calimyrna = Smyrna, Desert King = San Pedro; no invented homestead plates or Saline County ripen dates.

## Ban list

**Pass.** No hits for delve, landscape (non-dirt), robust, leverage, unlock, journey, Moreover/Furthermore stacks, game-changer, or the other STYLE_GUIDE bans in body copy.

## Prose and structure edits (by file)

| File | Change |
|------|--------|
| `drafts/08-lsu-champagne.md` | Quoted YAML `caption` (inner colon). |
| `drafts/09-lsu-tiger.md` | Quoted YAML `caption` (inner colon). |
| `drafts/16-panache.md` | Removed duplicate wood line in closing; wood rule stays in “How I run it.” |
| `drafts/17-desert-king.md` | Removed second `Wood:` block and redundant eat/relabel close; name-pile section keeps the type lesson. |
| `drafts/19-alma.md` | Quoted `meta_description` (inner colon). |
| `drafts/23-red-sicilian.md` | Closing pot-label only; drift triad kept once in “Flavor is a loaded shoot.” |
| `drafts/24-nuestra-senora-del-carmen.md` | Removed repeated [VERIFY]/eat/relabel block from closing. |
| `drafts/31-col-de-dame-blanc.md` | `green-necked` hyphenation; varied duplicate “museum of unfinished fruit” metaphor in closing. |
| `drafts/34-pastiliere.md` | Merged overlapping closing paragraphs (mail cuttings + pot labels). |
| `drafts/43-yellow-long-neck.md` | Removed repeated “looking forward” honesty line from pot-label close (kept in “What we refuse to fake”). |
| `drafts/44-syrian-dark-2.md` | Removed repeated “enough piles” sentence from pot-label line. |
| `drafts/45-maryland-berry.md` | Removed duplicate “photograph the cut once a year” from closing (kept in “What I will not write”). |

**No body edits** on the other 34 drafts: grammar clean, voice on-spec, word counts still 1,137–1,473 per `MANIFEST.md`.

## Front matter

- All 46 drafts: `voice_check: human` → **`voice_check: edited`**.
- `status: draft` unchanged.
- Opinions, tags, `fig_type`, and cultivar strings unchanged.

## House files

| File | Change |
|------|--------|
| `MANIFEST.md` | Voice line notes editor pass date. |
| `STYLE_GUIDE.md` | Documents `voice_check: edited` after human editor. |
| `EDITOR_REPORT.md` | This file. |

`INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_*`, `WP_IMPORT.md`, `README.md`, `SOURCES.md`: no edits (out of editor scope).

## Intentionally not changed

- Shared boilerplate across profiles (6–8 hours sun, UAEX souring, introduction-page links) — deliberate pack rhythm.
- Jack Lily / Jack Lilly dual spelling (interview + site usage).
- `[VERIFY]` placeholders where Saline County or plate proof is still open.
- Holding-profile honesty blocks on `43-yellow-long-neck.md` and `46-italian-258.md`.
- Optional `license: ""` on every `images:` block (template parity only; skipped to avoid 46-file YAML noise).

## Publish

**Do not publish to figroots.com from this branch.** WordPress **Draft** paste only, per `WP_IMPORT.md` and PR #319.
