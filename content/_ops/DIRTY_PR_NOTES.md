# DIRTY_PR_NOTES — supplements R&D blog pack (PR #245 cleanup)

**Date:** 2026-09-14  
**Scope:** `content/supplements-rd-blog/` (+ this ops note)  
**PR:** [#245](https://github.com/keithbbf-gif/cosmos/pull/245) (draft; do not merge from agent)

## What was dirty

1. **Wrong merge base.** PR #245 targeted `cursor/supplements-rd-blog-ee57` while a parallel editor line on `ee57` (PR #230) had already expanded all 40 drafts to ≥1,000 words, embedded PR #240 SVGs, and deduped figure blocks. GitHub reported **not mergeable** (divergent histories after `e346a43`).

2. **Stub / fork residue on the old #245 head (`9c98817`).** That branch kept **short** articles 17–40 (~466–743 words), **deleted** `assets/`, `scripts/embed_graphics.py`, `scripts/generate_graphics.py`, and stripped figure embeds from longform pieces (e.g. 03, 04, 06, 09). That is not publish-ready; it was a light editor pass on the pre-expansion pack.

3. **Competing `EDITOR_REPORT.md`.** Two incompatible reports would have conflicted on merge (one claimed PR #245, one PR #230 / ≥1k expansion).

4. **Swapped NEJM PMIDs (real citation bug).** VITAL vitamin D, VITAL marine n-3, and REDUCE-IT PMIDs were permuted (D2D `31173679` had been used for VITAL vitamin D). Wrong in `04`, `38`, `BIBLIOGRAPHY.md`, and the article-38 SVG footer.

5. **Minor copy fixes** from the light editor pass that still applied to the longform pack: COVID A to Z sentence (03), muscle-fiber CSA (06), ISSN cross-ref (35 → pieces 06 + 10).

## What we fixed (this cleanup)

| Action | Detail |
| --- | --- |
| Reconcile branch | Reset PR #245 line to **`origin/cursor/supplements-rd-blog-ee57`** (76c76ff): 40/40 ≥1,000 words, graphics pack + scripts retained |
| Rebase | Branch is **up to date with `main`** (no content conflicts) |
| PMID correction | **30415629** VITAL vitamin D; **30415637** VITAL n-3; **30415628** REDUCE-IT — in `04`, `38`, `BIBLIOGRAPHY.md`, `organism-vs-trial.svg`, `generate_graphics.py` |
| Stub removal | Did **not** merge `9c98817`; no short-draft or asset-stripped tree |
| Figure QA | All `![...](../assets/...)` paths resolve; duplicate figure blocks already removed on ee57 (03, 07, 13) |
| Ops doc | This file |

## Publish-ready checklist (pack)

- [x] 40 articles, `status: draft`, `voice_check: edited`
- [x] DSHEA disclaimer on all posts
- [x] Style-guide hard bans: clean (automated grep)
- [x] `ElitElixir` / `Unilever`: zero in `articles/`
- [x] Word floor ≥1,000 on all drafts
- [x] Graphics + embed scripts present
- [ ] Human/counsel: resolve `[CITE NEEDED]` / `[VERIFY]` before live import (`WP_IMPORT.md`)

## PR hygiene after push

- **Base branch** should be **`main`** (not `ee57`).
- **Head** updated on `cursor/supplements-rd-blog-editor-b6b8` (existing PR #245 head ref).
- PR #230 may overlap; reconcile with Keith whether to close #230 in favor of #245 or merge writer first.
