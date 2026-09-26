# DREAMS — buried farm outputs, indexed

1,328 WO dirs + 906 IN/WO prompts + 533 diffs (86.1 MB). Index: `DREAMS_INDEX.jsonl`. All tasks verbatim reuse; no new prompts written.

## Kinds
- pair (a/b blind, judge-ready): 78
- solo (single-seat saves): 353
- nodiff (json verdicts/empty): 897

## Pair dirs (78) — the COSMOS core dreams, blind-graded shape
- gitur-cdeck: 69
- gitur-cosmos: 9

Each pair dir: `cursor-a-001.json/.diff` + `cursor-b-001.json/.diff` — two independent mouths, same ITEM, no shared context. Judge compares a vs b (xor vs cofail). These feed the heroab A/B as baselines.

## Solo dirs (353)
- gitur-cosmos: 320
- gitur-cdeck: 33

Note: the `gitur-cosmos` solo bulk (320) is the furniture/history/blog/SEO content batch (e.g. PR #252 `cursor/furniture-fashion-fads-blog-a5c3` — 44 articles + 42 drafts, `Saved for Luna grading`). Content dreams, not COSMOS code — graded separately, never merged to core.
The 33 `gitur-cdeck` solos are core singles (cdeck panes, clocks, profiles/skins).

## IN/WO prompts (906)
`CREW/IN/WO/WO-001..906.md` — house-pack preload + ITEM tail (e.g. WO-001: Sessions Recents paint, ling propose + scout counter-propose, Luna grades). These are the prompt-tails behind the pairs.

## How they join the board
- 78 pair dirs → baselines for heroab requeues (same prompt + same agent + hero pack).
- 906 IN/WO → prompt library for WOMBAT ITEM authoring (verbatim reuse).
- 353 solos → content batch goes to Luna/content grading, never the code Judge.
- Score keys (`ab_pair_id`, `judge_score_hero/base/winner`) already on the 52 heroab rows in `WOMB_BOARD_AB_HERO.jsonl`.
