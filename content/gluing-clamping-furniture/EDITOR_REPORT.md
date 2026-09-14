---
title: Editor Report — Gluing & clamping furniture
status: draft
voice_check: edited
series: gluing-clamping-furniture
editor_branch: cursor/gluing-clamping-furniture-editor-3e25
writer_branch: cursor/gluing-clamping-furniture-175b
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/535
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in **PR #535** (`cursor/gluing-clamping-furniture-175b`). This branch stacks on that branch. Prose, cross-links, front matter, and pack QA only — no assets, no COSMOS core changes.

## Scope

| Area | Count |
|------|------:|
| Staged drafts (`d01`–`d48`) | 48 |
| Pack meta (`README.md`, `STYLE_GUIDE.md`, `INDEX.md`, …) | 8 |
| QA scripts (`scripts/recount_and_check.py`, `scripts/editor_pass.py`) | 2 |

All **48** numbered drafts now carry `voice_check: edited` in YAML front matter. `voice: human` unchanged. Pack index/README document the editor stamp.

## Method

1. Full-series read against `STYLE_GUIDE.md` — shop-floor voice, five stages, hard bans, no retelling `the-pot-on-the-hot-plate` / `clamps-then-quiet`, `[VERIFY]` discipline unchanged.
2. Automated banned-phrase scan (same regex as `scripts/recount_and_check.py`) — **no hits** in draft bodies before edit; none introduced.
3. **Cross-links:** replaced backtick `dXX` production pointers in **30** drafts with essay titles and numbers (e.g. `See *Cauls are the clamp you forgot* (essay 14).`) so import copy does not read like repo metadata. `STAGE.md` id list unchanged (editorial routing).
4. Line edit on awkward merged refs after substitution (**3** drafts): winter/August pointer, urea bag anecdote, cold-oak callback in essay 29.
5. `python3 scripts/recount_and_check.py` — word floors, YAML, bans, `voice_check` — **OK** (`45,526` body words).

## Notable edits

| Draft | Editor action |
| --- | --- |
| `d08-the-shop-at-fifty-degrees` | August cross-link punctuation (em dash, not nested parens) |
| `d29-winter-skin-august-flash` | Cold-oak callback wording (avoid “Hide on that rail is *Hide on cold oak…*”) |
| `d35-vacuum-bag-is-a-room-sized-clamp` | “like essay 4 told me to” → “as in *Urea is a different pot* (essay 4),” |
| **30 drafts with internal refs** | `dXX` → titled essay pointers (see git diff) |

Other drafts: read-aloud pass; shop register and writer judgments kept. No new `[VERIFY]` markers added or removed.

## Voice / shop floor

- Openings stay in the room (bottle, caul, clamp, smell). No thesis throat-clear added.
- Deliberate shop judgments kept (“biscuit is a spline you hope nobody measures,” gasket/creep language, South Arkansas humidity).
- Safety: `d47` remains a fume reminder, not a program; no new chemical how-to.

## Pack tooling

- `scripts/recount_and_check.py` — requires `voice_check: edited` or `voice_check: human` on every draft.
- `scripts/editor_pass.py` — idempotent stamp + ref humanizer (for reruns).
- `INDEX.md` — word counts synced to front matter after edit.

## QA command

```bash
python3 content/gluing-clamping-furniture/scripts/recount_and_check.py
```

## Handoff

Stack editor branch onto writer **PR #535** after review. **Draft PR; do not merge** without human sign-off. Import/publish remains out of scope.
