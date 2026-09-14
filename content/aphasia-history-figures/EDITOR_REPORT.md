---
title: Editor Report — SLPWOW Aphasia History & Figures
status: draft
voice_check: edited
series: slpwow-aphasia-history-figures
editor_branch: cursor/aphasia-history-figures-editor-9222
writer_branch: cursor/aphasia-history-figures-6c10
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/311
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #311 (`cursor/aphasia-history-figures-6c10`). Grammar, voice, duplication trims, and front matter only — no portrait downloads, no SVG, no WordPress publish.

## Scope

| Area | Count |
|------|------:|
| `articles/` | 45 |
| Pack meta touched | `INDEX.md`, `STYLE_GUIDE.md`, `check_pack.py` |

All 45 articles now carry `voice_check: edited` in YAML. Pack QA (`check_pack.py`) requires `edited` after this pass.

## Method

1. Full read against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md` (educational history; no treatment recipes; no generated faces).
2. Automated scan for STYLE_GUIDE hard bans (delve, landscape-as-boilerplate, Moreover stacks, etc.) — **no hits** in article bodies before edit; **none introduced** after edit.
3. Line edit for grammar, meta voice (“this pack” → “this article” where the frame was editorial), and trailing-section duplication where it repeated earlier paragraphs verbatim or near-verbatim.
4. **Claims:** no new statistics or sources; softened one strong “first at scale” line (Sarno) to “among the first…”
5. **Portraits / images:** unchanged notes-only policy; no binaries added.

## Notable edits (representative)

### Grammar / usage

- **07-the-1906-revision:** “a settled lecture notice it has” → “notices it has”; removed repeated imaging paragraph in trailing section.
- **18-jacques-lordat:** “a heir of Barthez” → “an heir of Barthez”.
- **05-the-house-diagram:** stray space before “Broca’s” in a quote clause.

### Voice / AI tics

- **01-the-word-that-would-not-come:** “the whole early history” → “runs through the early history”.
- **32-weisenburg-and-mcbride:** “That is the whole ethic…” → “That ethic is what later merchandise claimed to invent.”
- **21-paul-broca:** “This pack’s sibling series…” → stand-alone wording for the parallel profession series.

### Duplication / structure

- **16-childhood-and-the-word-aphasia:** trimmed trailing `## Bureaucracy is a theory` block that repeated Eisenson / Landau–Kleffner / disclaimer sentences; kept non-redundant closing.
- **27-jules-dejerine:** replaced near-copy of `## Reading as a separate architecture` in `## Print as a road` with a shorter coda on method and plates.
- **41-audrey-holland:** dropped repeated CADL/AphasiaBank setup in trailing section; kept humor/discourse paragraphs.
- **44-wilder-penfield:** removed trailing repeat of the 1959 atlas opening; kept ethics/homunculus closing with word-count-safe addition.

### Claims caution

- **40-martha-taylor-sarno:** “the first speech-language pathologist… at scale” → “among the first…”

### Meta voice (pack-wide)

- Replaced editorial **“this pack”** with **“this article”** in article bodies where the sentence was about editorial policy, not the folder path.
- **07-the-1906-revision:** “This series refuses the skip” → “An honest history refuses the skip.”

### Front matter / QA

- `voice_check: edited` on all 45 articles.
- `INDEX.md` voice-check note and article count (45) aligned with `check_pack.py`.
- `STYLE_GUIDE.md` documents writer `human` → editor `edited` handoff.
- `check_pack.py` gates on `voice_check: edited` and requires `EDITOR_REPORT.md`.

## Out of scope (by instruction)

- Fact-checking every birth/death year or attaching new bibliography entries.
- Portrait file downloads or graphics pass.
- Live WordPress import or scheduling (`stage: draft` unchanged).

## Treatment / faces audit

- **Treatment recipes:** none added; historical mentions of stimulation, MIT, partner training, etc. remain descriptive with explicit refusal to print protocols (unchanged intent).
- **AI faces:** no image files; portrait placeholders and `PORTRAIT_SOURCES.md` hunt notes unchanged; no synthetic-likeness language added.

## Sign-off

- **Voice:** magazine register per STYLE_GUIDE; hard bans clear.
- **QA:** `python3 content/aphasia-history-figures/check_pack.py` → **PASS** (45 articles).
- **PR:** draft only; do not merge without human review.
