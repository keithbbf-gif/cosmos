# Editor report — History of AI, Retrospective

**Pass date:** 2026-09-14  
**Branch:** `cursor/ai-history-editor-4bc7` (stacked on `cursor/ai-history-retrospective-7b08`, writer PR #256)  
**Editor:** Cloud agent (EDITOR role)  
**Graphics context:** PR #247 (unchanged by this pass)

## Verdict

**Proceed — not stubs.** Fifty-five essays and profiles are full magazine drafts (roughly 280–900 words each; series target 800–1,400). No HOLD for placeholder prose. Placeholder **portraits** (McCulloch, Winograd, Fukushima) are intentional and documented in `PORTRAIT_SOURCES.md`.

## Summary

| Metric | Count |
|--------|------:|
| Essays reviewed | 22 |
| Profiles reviewed | 33 |
| Pieces updated (`voice_check: edited`) | 55 |
| Hard-ban phrase hits (post-pass) | 0 |
| Out-of-scope name hits in body copy | 0 |
| Figure / portrait embeds preserved | all |
| `portrait` / `portrait_status` front matter preserved | all |

## What was fixed

1. **Grammar and clarity (targeted)** — Examples: McCarthy lede (`intervening years`, `at Stanford`, article before “furniture”); Hinton 2012 line (`his students’ engineering victory`); robotics essay (Nilsson attribution; subject–verb agreement on the Stanford Cart sentence).
2. **Front matter** — Set `voice_check: edited` and `voice_check_date: 2026-09-14` on every essay and profile.
3. **Ban list** — Scanned essay and profile bodies for `STYLE_GUIDE.md` banned habits (delve, landscape-as-metaphor, leverage, robust, seamless, tapestry, throat-clearing Moreover/Importantly). No hits.
4. **Novelty** — Confirmed no COSMOS, KMesh, ModelRater, or house-system names in essay/profile bodies (guardrails doc only).
5. **Preserved** — All `![…](../assets/…)` embeds, portrait credit lines, labeled SVG placeholders, `portrait_status: placeholder` blocks, and PHOTO_NOTES / PORTRAIT_SOURCES cross-references.

## Remaining weak spots

- **Length** — Many profiles sit below the 800-word style target. They read complete as short portraits; a writer expansion pass could deepen bench-era detail where desired.
- **Graphics stack** — This editor branch does not include figure SVGs from #247. Merge writer → graphics → editor (or rebase editor onto graphics) before WP import if diagrams must ship together.
- **Portrait gaps** — McCulloch, Winograd, and Fukushima remain labeled placeholders until Commons-sourced likenesses clear `PORTRAIT_SOURCES.md` criteria.

## Articles that still risk “AI” read (lower confidence)

These are already on-voice but structurally similar (short profile arc: scene → papers → consequence):

| Slug | Note |
|------|------|
| `david-rumelhart` | Compact; PDP and *Nature* letter could use one more scene sentence if length is required. |
| `kunihiko-fukushima` | Placeholder panel dominates; prose is paper-forward by design. |
| `demis-hassabis` | Correctly refuses corporate biography; may feel thin next to longer game essays. |

No piece was left with stub boilerplate or empty sections.

## Not in scope

- No changes to `assets/portraits/` binaries or placeholder SVGs.
- No `BIBLIOGRAPHY.md` additions (no new factual claims introduced).
- No COSMOS / live-tree / product documentation.
