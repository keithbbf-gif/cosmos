---
title: Editor report — Open-Source AI, 2015–2026
status: draft
voice_check: edited
series: open-source-ai-history-2015-2026
editor_pass: 2026-09-14
pr: 347
---

# Editor report

Editor pass on the staged pack in `content/open-source-ai-history-2015-2026/` for PR #347. **Novelty-safe:** public first-party history only; no COSMOS, mesh, or private-stack claims. **Voice:** peer shop tone per `STYLE_GUIDE.md`; no new product pitch.

## Scope

- 46 canonical drafts (`writer-slugs.json`)
- Series meta: `INDEX.md`, `MANIFEST.md`, `STYLE_GUIDE.md`, `README.md`, `BIBLIOGRAPHY.md`, `SERIES_MAP.md`, `GRAPHICS_INDEX.md`
- QA harness: `check_pack.py`
- Figures and `staged-embeds/` unchanged (SVG well-formedness from prior commit retained)

## Summary

| Check | Result |
|-------|--------|
| `python3 check_pack.py` | OK — 46 drafts, 43,803 body words |
| COSMOS / `cosmos` in drafts | None |
| Banned phrase scan (extended) | Clean |
| `voice_check: edited` on all drafts | Set |
| Figures pasted per `GRAPHICS_INDEX.md` | Nine illustrated drafts unchanged |

## Changes made

### Pack-wide

1. **`voice_check: human` → `voice_check: edited`** on all 46 drafts and series markdown frontmatter.
2. **Markdown hygiene:** blank line before `## Sources` in `intro-the-open-stack`, `before-tensorflow-theano-torch-caffe`, and `tensorflow-november-2015`.
3. **`check_pack.py`:** require `voice_check: edited`; extend banned list with `revolution`, `journey`, `elevate`, `empower` (STYLE_GUIDE alignment).
4. **`STYLE_GUIDE.md`:** note that editor pass sets `voice_check: edited` and records the pass here; writer template still shows `voice_check: human`.
5. **`MANIFEST.md` / `INDEX.md`:** counts and pointers to this report.

### Article-level prose

| Slug | Edit |
|------|------|
| `pytorch-2016-define-by-run` | Heading: “DataLoader as a quiet revolution” → “DataLoader without graph queues” (banned noun). |
| `twenty-twenty-six-the-stack` | Capstone meta-instruction rephrased for reader (“This pack does not invent a September headline…”). |
No other drafts required structural rewrites. Ledes, license spine, and cross-links were left intact.

## Novelty and boundary (explicit)

- No new architectural claims, no unpublished mechanisms, no COSMOS/KDash/private OS references.
- Uncertain dates remain `[CITE NEEDED]` (see `intro-the-open-stack`, `chinese-open-weight-wave`, `qwen-alibaba-stack`, `twenty-twenty-six-the-stack`).
- Vendor superlatives stay quoted or attributed; narrator does not rank models.

## Remaining for author / fact-check

1. **`[CITE NEEDED]`** markers — pin or trim before publish.
2. **2026 model cards** named in `twenty-twenty-six-the-stack` — verify against first-party posts at import time (Mistral Small 4, Qwen3.6, DeepSeek-V4 Preview, Gemma 4, etc.).
3. **Yi license drift** — `chinese-open-weight-wave` documents Hub snapshot disagreement; re-open `LICENSE` on pin.
4. **Macquoid aside** — intentional series voice in `intro-the-open-stack` and `what-a-license-actually-permits`; keep or cut for audience.

## QA command

From repo root or this directory:

```bash
python3 content/open-source-ai-history-2015-2026/check_pack.py
```

Expected: `OK`.
