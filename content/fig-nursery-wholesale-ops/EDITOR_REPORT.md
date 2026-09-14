# Fig nursery / wholesale ops — EDITOR_REPORT

**Stream:** EDITOR (`content/fig-nursery-wholesale-ops/`)  
**Writer PR:** #386 (`cursor/fig-nursery-wholesale-ops-660b`, staged buyfigs pack)  
**Date:** 2026-09-14  
**Editor outcome:** `voice_check: edited` on **all 46** staged drafts  

## Gate (46-draft pack)

| Check | Result |
| --- | --- |
| Draft count | **46** markdown drafts (`d01`–`d46`) |
| `validate.py` | **PASS** — stages, manifest keep-ids, word floors, slop/medical scan |
| Body word count | **520–608** words each; **24,981** total body words |
| Claims policy | **no-medical** enforced by validator; intentional refusals kept (`d34`, `d45`, `d22`, `d09`) |
| SERIES / slop needles | **0** hits on banned slop/medical phrases in bodies |
| Thin / outline-only | **No** |
| Decision | Full buyfigs bench voice pass; light copy edits — writer pack was desk-ready |

No new articles were invented. No stubs were padded. `validate.py`, `_manifest.toml`, and `IMAGE_SOURCES` (none in pack) were not rewritten.

## What changed

### Pack-wide

- Set **`voice_check: edited`** in YAML front matter on all **46** drafts.
- **`MANIFEST.md`:** last validate line notes editor `voice_check: edited`.
- **`STAGE.md`:** documents `voice_check: edited` on staged drafts.

### Targeted copy (grammar / buyfigs bench voice)

| File | Notes |
| --- | --- |
| `d02-dormant-window-is-the-product.md` | Jack first person: “I already wrote the test on FigRoots” (not third-person Jack) |
| `d05-grade-is-a-promise.md` | Article fix: “A **long** or **liner** grade” |
| `d10-polarity-on-the-bench.md` | “My read-a-cutting draft on FigRoots” (sender/receiver split) |
| `d11-name-goes-on-before-the-cut.md` | “My FigRoots labeling habit” (bench voice) |
| `d12-three-labels-or-you-will-lie.md` | “My grower post … an Arkansas summer” (article + first person) |
| `d29-cooler-is-a-delay-not-a-hospital.md` | “My fridge post on FigRoots” |
| `d44-doa-is-a-clock.md` | “I already wrote that for growers on FigRoots” |
| `d46-the-season-on-one-wall.md` | “an honest dormant wholesale” |

### Intentionally preserved

- **PapaFig** drafts that cite “Jack’s …” on FigRoots (`d04`, `d17`, `d34`, `d45`, `d40`) — correct two-voice bench.
- Plant sanitation vs human medicine boundaries (`d09`, `d22`, `d45`, `d34`).
- `[VERIFY]` on agency/state/USPS claims.
- `status: staged`, six trade stages (`take` → `land`), keep-four ids (`d12`, `d19`, `d35`, `d45`).
- Jack / PapaFig author tags and cluster topics.

## QA checklist (editor)

- [x] 46 files, each `voice_check: edited`
- [x] `python3 validate.py` passes with **0** errors
- [x] No new medical or supplement claims introduced
- [x] No live-publish steps added
- [x] Stacked PR targets writer branch for #386, not `main`

## Handoff

- **Fact desk:** phytosanitary / state soil rules remain `[VERIFY]`; no certificate language added.
- **Publisher:** files stay **`status: staged`** until Keith schedules.
- **Merge:** draft PR only — do not merge without Keith.
