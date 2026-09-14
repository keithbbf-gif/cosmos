---
title: Editor Report — WOW Therapies Group-Therapy History
status: draft
voice_check: edited
series: wowtherapies-group-therapy-history
editor_branch: cursor/group-therapy-history-editor-ecf0
writer_branch: cursor/group-therapy-history-59bb
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/461
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #461 (`cursor/group-therapy-history-59bb`). Grammar, voice, meta-frame tightening, and front matter only — no portrait downloads, no graphics, no WordPress publish.

## Scope

| Area | Count |
|------|------:|
| `articles/` | 44 |
| Pack meta touched | `INDEX.md`, `MANIFEST.md`, `check_pack.py`, `EDITOR_REPORT.md` |

All 44 articles now carry `voice_check: edited` in YAML. Pack QA (`check_pack.py`) requires `edited` after this pass.

## Method

1. Full read against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md` (educational history; no treatment recipes; no generated faces).
2. Automated scan for STYLE_GUIDE hard bans (`check_pack.py` regex list) — **no hits** in article bodies before edit; **none introduced** after edit.
3. Line edit for grammar and meta voice: editorial **“this pack”** in article bodies → **“this essay,” “this series,”** or a named ops file (`INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_NOTES.md`) where the frame was folder metadata, not the reader’s subject.
4. **Claims:** no new statistics or sources; `[CITE NEEDED]` / `[VERIFY]` markers unchanged in intent.
5. **Portraits / images:** unchanged notes-only policy; no binaries added.

## Notable edits (representative)

### Voice / meta frame

- Pack-wide: replaced in-body **“this pack”** / **“this pack’s”** with **“this series,” “this essay,”** or explicit file names so public prose does not sound like a repo README (44 files; `MANIFEST.md` / `INDEX.md` pack language unchanged where it describes the folder).
- **01-before-the-circle:** “This pack names the theft” → “This essay names the theft.”
- **13-structured-cbt-groups:** “Guardrails for this series” → “The claims guardrails.”
- **28-michael-balint:** “The group-therapy pack is not a second Freud biography” → “This series is not a second Freud biography.”
- **37-gisela-konopka:** “the pack bibliography” → “BIBLIOGRAPHY.md.”
- **44-dorothy-stock-whitaker:** “the pack’s working date” → “the index’s working date.”

### Claims / protocols

- No new session scripts, icebreakers, worksheets, or “try this” counsel added.
- Historical mentions of manuals, Steps, psychodrama, encounter heat, and cohesion research remain descriptive with explicit refusal to print protocols (unchanged intent; spot-checked across era essays 04, 08, 09, 11, 13, 16 and figure essays 18–20, 42).

### Sibling-series pointers

- Cross-references to `content/wowtherapies-therapy-history/` and SLPWOW (“individual psychotherapy-history pack,” “consulting-room pack”) **kept** where they document deliberate non-duplication; no sentence copying from those packs.

### Front matter / QA

- `voice_check: edited` on all 44 articles.
- `INDEX.md` voice-check note aligned with `check_pack.py`.
- `check_pack.py` gates on `voice_check: edited` and requires `EDITOR_REPORT.md`.

## Out of scope (by instruction)

- Fact-checking every birth/death year or attaching new bibliography entries.
- Portrait file downloads or graphics pass.
- Live WordPress import or scheduling (`status: publishable` unchanged in YAML; PR remains draft).

## Treatment / faces audit

- **Treatment recipes:** none added; historical method names stay dated and refused as how-tos.
- **AI faces:** no image files; portrait placeholders and `PORTRAIT_SOURCES.md` hunt notes unchanged.

## Sign-off

- **Voice:** magazine register per STYLE_GUIDE; hard bans clear.
- **QA:** `python3 content/group-therapy-history/check_pack.py` → **PASS** (44 articles).
- **PR:** draft only; do not merge without human review.
