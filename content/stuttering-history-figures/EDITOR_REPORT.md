---
title: Editor Report — SLPWOW Stuttering & Fluency History
status: draft
voice_check: edited
series: slpwow-stuttering-history-figures
editor_branch: cursor/stuttering-history-editor-6370
writer_branch: cursor/stuttering-history-figures-f6ca
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/394
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #394 (`cursor/stuttering-history-figures-f6ca`). Grammar, voice, duplication trims, and front matter only — no portrait downloads, no SVG, no WordPress publish.

## Scope

| Area | Count |
|------|------:|
| `articles/` | 45 |
| Pack meta touched | `INDEX.md`, `STYLE_GUIDE.md`, `check_pack.py`, `EDITOR_REPORT.md` |

All 45 articles now carry `voice_check: edited` in YAML. Pack QA (`check_pack.py`) requires `edited` after this pass.

## Method

1. Full read against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md` (educational history; no treatment recipes; no generated faces).
2. Automated scan for STYLE_GUIDE hard bans (delve, landscape-as-boilerplate, Moreover stacks, etc.) — **no hits** in article bodies before edit; **none introduced** after edit.
3. Line edit for grammar, meta voice (“this pack” → “this article” / “this series” / “this profile” where the frame was editorial), and one operant-era usage fix.
4. **Claims:** no new statistics or sources; date-uncertainty language unchanged in intent.
5. **Portraits / images:** unchanged notes-only policy; no binaries added.

## Notable edits (representative)

### Grammar / usage

- **11-the-operant-years:** “The speaker who fluent-for-tokens” → “The speaker who was fluent for tokens and stammered for life.”

### Voice / meta frame

- Pack-wide: replaced editorial **“this pack”** in article bodies with **“this article,” “this essay,” “this profile,”** or **“this series”** as context required (45 files; meta README/INDEX pack language unchanged where it describes the folder).
- **06-iowa-builds-a-laboratory:** “This pack has him as…” → “This essay keeps him as…”
- **05-berlin-and-vienna:** “This pack tells it…” → “This essay tells it…”
- **29-wendell-johnson:** “This pack has the cause…” → “This profile keeps the cause…”
- **17-demosthenes:** “This pack’s era essay…” → “The era essay…”
- **16-icf-stigma-and-who-was-left-out:** “when we have it” → “when known” (living-figure preference line).

### Structure

- **41-c-woodruff-starkweather:** moved the Temple/demands-capacities closing paragraph above the “Published work only…” guardrail so the section order reads argument → coda → compliance line → Portrait.

### Sibling-series pointers

- Cross-references to `content/slpwow-speech-pathology-history/` (“sibling profession pack”) **kept** where they document deliberate non-duplication; no sentence copying from that pack.

### Front matter / QA

- `voice_check: edited` on all 45 articles.
- `INDEX.md` voice-check note aligned with `check_pack.py`.
- `STYLE_GUIDE.md` documents writer `human` → editor `edited` handoff.
- `check_pack.py` gates on `voice_check: edited` and requires `EDITOR_REPORT.md`.

## Out of scope (by instruction)

- Fact-checking every birth/death year or attaching new bibliography entries.
- Portrait file downloads or graphics pass.
- Live WordPress import or scheduling (`stage: draft` unchanged).

## Treatment / faces audit

- **Treatment recipes:** none added; historical mentions of Lidcombe, GILCU, prolonged speech, DAF, Hollins, etc. remain descriptive with explicit refusal to print protocols (unchanged intent).
- **AI faces:** no image files; portrait placeholders and `PORTRAIT_SOURCES.md` hunt notes unchanged; no synthetic-likeness language added.

## Sign-off

- **Voice:** magazine register per STYLE_GUIDE; hard bans clear.
- **QA:** `python3 content/stuttering-history-figures/check_pack.py` → **PASS** (45 articles).
- **PR:** draft only; do not merge without human review.
