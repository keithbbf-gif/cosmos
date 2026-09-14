# Editor report — fig propagation & rooting

**Date:** 2026-09-14  
**Scope:** `content/fig-propagation-rooting/` (46 drafts + house files)  
**Upstream:** PR #407 (`cursor/fig-propagation-rooting-4bb7`)  
**Editor branch:** `cursor/fig-propagation-rooting-editor-50c1` (stacked on writer PR #407)  
**Gate:** `voice_check: edited` on all 46 drafts  
**Validation:** `python3 content/fig-propagation-rooting/validate.py` → **PASS** (46 drafts; 666–900 words each; 34,897 body words total)

## Method

1. Read `README.md` and `STAGE.md` (Jack vs PapaFig pens, Zone **8a**, staged status, published numbers we do not restage).
2. Full read of 20 representative drafts across all four stages; skim of all 46 for slop phrases, YAML, author lines, and intra-file repetition.
3. Ran `validate.py` before and after (46 drafts, ≥600 body words, stage coverage, topic needles).
4. Automated scan: `validate.py` slop list, duplicate-sentence detection within files, cross-file paragraph duplication.
5. **Preserved on purpose:** industry stick **6–8" / three nodes**; 2023 coir/DE counts cited as *that* test (64/64, 60/64); thermostat **75–78°F** / probe in mix; Jack’s “Dad” lines for PapaFig/Keith; `[VERIFY]` county frost placeholders; deliberate pack rhythm (pot-up before June, August hold, established = two summers).

## Ban list / slop

**Pass.** No hits for the `validate.py` slop phrases or common AI filler in body copy.

## Voice (Jack / PapaFig)

| Pen | Drafts | Check |
| --- | --- | --- |
| Jack Chambers | d01–d38 (cutting, rooting, air-layer) | Concrete first; heat mats, pops, layers; cites PapaFig/Dad for trials and pot ops without speaking as PapaFig. |
| PapaFig | d39–d46 (transplant / in-ground) | Pot-up, clay mound, established, suckers; hundreds of pots / ~25–30 in clay; no “Dad” first person. |

**Pass.** Author YAML matches body pen. Cross-voice references (e.g. d17 Jack citing PapaFig’s A/B writeup, d46 PapaFig citing Jack’s “first two summers”) kept.

## Prose and structure edits (by file)

| File | Change |
| --- | --- |
| `drafts/d41-clay-hole-not-a-grave.md` | Removed duplicate late-winter/spring vs August hero-plant sentence (kept in mound paragraph). |
| `drafts/d35-how-long-before-you-cut-it-free.md` | Trimmed repeated “morning cut / damp pot” setup in cut-free section. |
| `drafts/d24-hormone-is-optional.md` | Replaced awkward `[VERIFY]ing the label` with plain “reading the label again.” |
| `drafts/d46-what-established-means-in-8a.md` | Tightened closing notebook paragraph; dropped repeated pot-up / August / yard-count lines already stated above. |

**No body edits** on the other 42 drafts: grammar clean, voices on-spec, word counts **666–900** (34,897 total body words per `validate.py`).

## Front matter

- All 46 drafts: added **`voice_check: edited`** (after `voice: human`).
- `status: staged` unchanged.
- Authors, stages, clusters, topics, and image paths unchanged.

## House files

| File | Change |
| --- | --- |
| `STAGE.md` | Documents `voice_check: edited`; staged definition updated. |
| `README.md` | Staged blurb notes editor pass. |
| `validate.py` | Requires `voice_check: edited` on each draft. |
| `EDITOR_REPORT.md` | This file. |

`INDEX.md`, `PHOTO_NOTES.md`, `_manifest.toml`: no edits (out of editor scope).

## Intentionally not changed

- Shared closing beats across the set (pot-up before June, August hold, two summers established) — deliberate magazine rhythm, not accidental paste.
- `[VERIFY]` frost lines (Saline County vs reader county) — still open for Keith.
- Jack referring to PapaFig as “Dad” in Jack-authored pieces.
- d38 potting-hour voice stays Jack (air-layer cut-to-pot); d39+ stay PapaFig for cup-to-#3 and holes.

## Publish

**Do not publish to figroots.com from this branch.** Staged copy only; WordPress **Draft** if pasted. Merge editor PR into #407 only after human review — **no auto-merge.**
