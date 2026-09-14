---
title: Editor report — public AI safety discourse
status: draft
voice_check: edited
series: ai-safety-public-discourse
editor_pass: 2026-09-14
pr: 396
---

# Editor report

Editor pass on `content/ai-safety-public-discourse/` for PR #396. **Novelty-safe:** public-record recap only; no COSMOS, mesh, or private-stack claims. **Voice:** careful adult walking a reader through primary pages; `voice_check: edited` on every markdown file in the folder.

## Scope

| Class | Count |
| --- | --- |
| Numbered drafts (`01`–`52`) | 52 |
| How-to (`00`) | 1 |
| Series meta | `README.md`, `INDEX.md`, `MANIFEST.md`, `SOURCES.md`, this report |
| QA | `check_pack.py` |

## Summary

| Check | Result |
| --- | --- |
| `python3 check_pack.py` | OK — 53 numbered/how-to body files; 25,742 body words (00 + 01–52) |
| COSMOS / house names in folder | None |
| Banned AI habit phrase scan | Clean (official *robustness* vocabulary retained on purpose) |
| `voice_check: edited` | Set on all 58 markdown files (53 essays + 5 meta + this report) |
| Novelty footer on `00` + `01`–`52` | Present |

## Changes made

### Pack-wide

1. **`voice_check: edited`** added to frontmatter on every file (writer staging used `voice: human` only).
2. **`check_pack.py`** — file count, series tags, novelty footer, body-word band (280–850), house-name ban, habit-phrase scan; requires this report.
3. **`SOURCES.md`** — linked URLs for the March 2023 FLI pause letter and May 2023 CAIS statement.
4. **`MANIFEST.md` / `INDEX.md` / `README.md`** — pointers to this report and the QA command.

### Article-level prose

| File | Edit |
| --- | --- |
| `00-how-to-read-this-set.md` | Fact-check line: "sentence of mine" → "sentence in these drafts" (distance from narrator-as-authority). |
| `25-stop-competing-clause.md` | Classroom prompt: "empowered to apply" → "may apply" (plain predicate, no habit diction). |
| `51-media-frames-2014-2024.md` | Fixed frame count: "seventh" / "Seven" → **sixth** / **Six** (five named frames plus anniversary habit). |
| `44-letters-2023-pause-and-cais.md` | `sources:` block with public letter URLs (aligned with `SOURCES.md`). |

No merges, no new claims, no cuts to the four-spine structure. Ledes and cross-references between drafts were left intact.

## Novelty and boundary (explicit)

- No new safety framework, metric, or policy proposal.
- No unpublished correspondence, board material, or internal product names.
- Open letters, charters, and the EU file are described as **speech acts** or **instruments** at the appropriate force level; drafts do not upgrade them.
- Essay `52-what-this-set-leaves-out.md` keeps the host repository out of scope by design.

## Remaining for author / fact-check

1. **Signature counts** on 2015–2023 letters — date any count at time of reading; pages change.
2. **OpenAI blog URLs** — prefer live charter/founding posts or Wayback pins before import (`SOURCES.md` lists examples).
3. **EO 14110** — note revocation (January 2025) whenever the order is assigned; draft `45` and `50` mention it but a publish gate should re-open the Federal Register line.
4. **Word band** — `check_pack.py` enforces 280–850 body words per `00`/`01`–`52`; `00` is at the top of the band. If a later pass adds material, split or trim before publish.

## QA command

From repo root or this directory:

```bash
python3 content/ai-safety-public-discourse/check_pack.py
```

Expected: `OK`.
