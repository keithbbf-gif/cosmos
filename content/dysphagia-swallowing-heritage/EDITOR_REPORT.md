---
title: Editor Report — SLPWOW Dysphagia & Swallowing Heritage
status: draft
voice_check: edited
series: slpwow-dysphagia-swallowing-heritage
editor_branch: cursor/dysphagia-editor-6c95
writer_branch: cursor/dysphagia-swallowing-heritage-90b7
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/420
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #420 (`cursor/dysphagia-swallowing-heritage-90b7`). Grammar, voice, duplication trims, and front matter only — no portrait downloads, no graphics, no WordPress publish. Educational history only; no treatment protocols.

## Scope

| Area | Count |
|------|------:|
| `articles/` | 44 |
| Pack meta touched | `INDEX.md`, `STYLE_GUIDE.md`, `WP_IMPORT.md`, `check_pack.py` |

All 44 articles now carry `voice_check: edited` in YAML. Pack QA (`check_pack.py`) requires `edited` after this pass and expects this file at pack root.

## Method

1. Full read against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md` (magazine register; no DIY swallow programs; no generated faces).
2. Automated scan for STYLE_GUIDE hard bans (`delve`, `healthcare landscape`, `whether you're a`, etc.) — **no hits** in article bodies before edit; **none introduced** after edit.
3. Line edit for grammar and for editorial meta voice (`this pack` → `this essay` / `this profile` / `this series` where the sentence was about staging policy, not folder paths).
4. **Claims:** no new statistics or bibliography entries; historical mentions of maneuvers, IDDSI, water protocols, and screens remain descriptive with explicit refusal to print steps or household recipes (unchanged intent).
5. **Portraits / images:** unchanged notes-only policy; no binaries added.

## Notable edits (representative)

### Meta voice (pack-wide)

- Replaced **“this pack”** framing in article bodies with **this essay**, **this profile**, or **this series** (and **when these drafts were staged (September 2026)** for living-figure staging lines).
- **20-chevalier-jackson:** sibling split with voice-disorders heritage as **series** wording, not “pack meets pack.”
- **22-arthur-hurst:** `meta_description` uses **this profile** instead of **this pack**.

### Duplication / structure

- **16-what-a-swallow-study-became:** removed a near-duplicate rewind paragraph under “Who was left out”; merged the stronger pause-button close into **Residue**.
- **24-martin-w-donner:** dropped a repeated German-born / Deutsche Röntgengesellschaft paragraph; kept one CV block and the Hopkins-center sentence.
- **44-olle-ekberg:** removed a repeated “several birth certificates” block under **What later people kept** (already covered above).

### Grammar / usage

- **36-reza-shaker:** residue sentence — **therapy-gym mat this profile will not teach anyone to use** (cleaner than a stranded relative clause).

### Front matter / QA

- `voice_check: edited` on all 44 articles.
- `INDEX.md` voice-check note aligned with editor handoff.
- `STYLE_GUIDE.md` documents writer `human` → editor `edited` handoff.
- `WP_IMPORT.md` — do not expose `voice_check` on the public site.
- `check_pack.py` gates on `voice_check: edited` and requires `EDITOR_REPORT.md`.

## Out of scope (by instruction)

- Fact-checking every birth/death year or attaching new bibliography entries.
- Portrait file downloads or graphics pass.
- Live WordPress import or scheduling (`stage: draft` unchanged).

## Treatment / faces audit

- **Treatment recipes:** none added; mentions of chin tuck, Shaker, IDDSI, Frazier water protocols, TOR-BSST, MBSImP, etc. remain historical with explicit “will not print” lines where needed.
- **AI faces:** no image files; portrait placeholders and `PORTRAIT_SOURCES.md` hunt notes unchanged; no synthetic-likeness language added.

## Sign-off

- **Voice:** magazine register per STYLE_GUIDE; hard bans clear.
- **QA:** `python3 content/dysphagia-swallowing-heritage/check_pack.py` → **PASS** (44 articles).
- **PR:** draft only; do not merge without human review.
