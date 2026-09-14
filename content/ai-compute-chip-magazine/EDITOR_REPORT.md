---
title: Editor report — AI Compute Chip Magazine
status: staged
voice_check: edited
series: ai-compute-chip-magazine
editor_pass: 2026-09-14
pr: 404
---

# Editor report

Editor pass on the staged pack in `content/ai-compute-chip-magazine/` for PR #404. **Novelty-safe:** public-record GPU/CUDA/TPU history only; no COSMOS, mesh, or private-stack claims. **Voice:** magazine peer tone per `STYLE_GUIDE.md`; no product pitch.

## Scope

- 45 canonical drafts (`writer-slugs.json`)
- Series meta: `INDEX.md`, `STYLE_GUIDE.md`, `writer-slugs.json`
- QA harness: `check_pack.py`

## Summary

| Check | Result |
|-------|--------|
| `python3 check_pack.py` | OK — 45 drafts, 27,104 body words |
| COSMOS / `cosmos` in draft bodies | None |
| Banned phrase scan (body, pre-Sources) | Clean after prose fixes |
| `voice_check: edited` on all drafts | Set |
| OSS history pack (`PR #347`) | Already edited — not touched this pass |

## Changes made

### Pack-wide

1. **`voice_check: edited`** added to all 45 article frontmatter files.
2. **`STYLE_GUIDE.md`**, **`writer-slugs.json`**, **`check_pack.py`** — QA aligned with the open-source AI history editor pattern (500–1,200 word band, banned list, staged status).
3. **`INDEX.md`** — editor pass note and masthead pointer to this report.

### Article-level prose

| Slug | Edit |
|------|------|
| `06-ian-buck-walks-into-santa-clara` | “unlock a card” → “drive a card” (banned verb). |
| `08-g80-the-unified-shader` | “order of their revolutions” → “order of their turns”. |
| `14-pascal-p100-hbm2-nvlink` | “quieter/louder revolution” → “quieter/louder shift” (×2). |

No other drafts required structural rewrites. Ledes, first-person asides, and source lists were left intact.

## Novelty and boundary (explicit)

- No new architectural claims, no unpublished mechanisms, no COSMOS/KDash/private OS references.
- Staged means facts and citations can still be tightened before publish.
- Vendor launch titles in `## Sources` may quote marketing words the body avoids.

## Remaining for author / fact-check

1. Pin archived URLs on high-traffic sources (GeForce 256, CUDA Nov 2006, DGX-1 Apr 2016) where only prose citations exist today.
2. Reconcile public CUDA SDK ship dates vs. November 8, 2006 naming (called out in `07-november-8-2006-cuda-gets-a-name`).
3. Blackwell and Hopper specs — re-read against current product pages before any import.

## QA command

From repo root or this directory:

```bash
python3 content/ai-compute-chip-magazine/check_pack.py
```

Expected: `OK`.
