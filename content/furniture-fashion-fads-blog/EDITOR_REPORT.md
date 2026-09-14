---
title: Editor Report — Furniture Fashion & Fads
status: draft
voice_check: edited
series: furniture-fashion-fads
editor_branch: cursor/furniture-fashion-fads-blog-editor-5d4d
writer_branch: cursor/furniture-fashion-fads-blog-a5c3
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/252
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #252 (`cursor/furniture-fashion-fads-blog-a5c3`). This branch stacks on that branch; prose and front matter only — no SVG or asset changes.

## Scope

| Area | Count |
|------|------:|
| `articles/` | 44 |
| `drafts/` | 42 |
| **Total markdown essays** | **86** |
| Embedded `<figure class="fffb-figure">` blocks | 68 |
| `[CITE NEEDED]` markers (left intact) | 119 |

All 86 essays now carry `voice_check: edited` in YAML front matter. Pack meta files (`STYLE_GUIDE.md`, `INDEX.md`, manifests) were not re-voiced; they remain `voice_check: human` for the writer/editor split.

## Method

1. Full read against `STYLE_GUIDE.md` (voice, hard bans, fact rules).
2. Automated scan for banned AI lexicon (delve, landscape-as-metaphor, Moreover/Furthermore stacks, etc.) — **no hits** in essay bodies.
3. Spell/grammar pass (codespell + line edit); fixed article/draft-specific issues only where flagged.
4. **Figure integrity:** every `<figure>...</figure>` block in `articles/` and `drafts/` was compared byte-for-byte to the writer branch (`origin/cursor/furniture-fashion-fads-blog-a5c3`) — **0 mismatches**.
5. **Citations:** no new statistics, quotes, or primary sources added; all `[CITE NEEDED]` markers preserved.

## Notable edits (representative)

### Meta / AI tics

- Removed or varied fourth-wall closers (“That is the whole essay / comparison / cycle”) in drafts **05**, **13**, **19** and articles **cargo-pants-resurgence**, **conversation-pit-revival**, **fast-furniture-vs-fast-fashion**.
- Softened repeated bbfur contrast template (“looks almost rude/stubborn … is useful”) in **tiktok-shelf-life** and **ikea-x-fashion-crossover**.

### Grammar / usage

- **peplum-waistline:** “a hourglass” → “an hourglass”.
- **neon-sign-home-decor:** “a even” → “an even”.
- **rattan-everywhere-phases**, **draft 20:** “an 1980s” → “a 1980s”.
- **ikea-era-flat-pack:** “delivery men” → “deliverymen”.
- **logomania-waves:** “pair of Gucci loafer” → “loafers”.
- **normcore-ironically-timeless:** “tee shirt” → “T-shirt”.
- **draft 03:** “walnut dingbat” → “walnut Danish”.
- **draft 10:** “a owner” → “an owner”.
- **draft 19:** “a ‘old world’” → “an ‘old-world’”.
- **draft 22:** “an 1987” → “a 1987”; tightened “What leftover was”.
- **draft 35:** “a airline” → “an airline”.
- **y2k-fashion-revival:** clarified “logo’s fake” line (“a hint of counterfeit”).

### Structure / duplication

- **draft 29 (leather club):** merged duplicate Victorian-club / RH retail setup into one paragraph.
- **draft 37 (vintage market):** dropped repeated Mediterranean-oak ticker (kept in opening).

### Front matter

- `word_count` recalculated from body text (after `---` block) on all 86 files where the YAML count had drifted from the writer pass.

## Out of scope (by instruction)

- Fact-checking and attaching sources for `[CITE NEEDED]` — deferred.
- `WP_IMPORT.xml`, `embeds/`, `graphics-manifest.json`, SVG assets — untouched.
- Scheduling, categories, or live WordPress publish — still draft-only per `INDEX.md`.

## Commits on this branch

Stacked editor commits (grammar/voice/`voice_check`/`word_count`) on top of writer PR #252. See `git log cursor/furniture-fashion-fads-blog-editor-5d4d` for the full list.

## Sign-off

- **Figures:** preserved exactly (verified against writer branch).
- **Voice:** human magazine register; STYLE_GUIDE hard bans clear.
- **Facts:** no invented numbers; cite gaps explicitly marked.
