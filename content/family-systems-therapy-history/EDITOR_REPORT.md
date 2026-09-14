# Editor report — family-systems therapy history pack

**Editor pass:** 2026-09-14  
**PR:** #447 (`cursor/family-systems-therapy-history-02ad` / editor branch)  
**Scope:** All 44 staged essays + ops cross-check. Educational history only; no protocols added or restored.

## Stamp

| Gate | Result |
| --- | --- |
| `python3 content/family-systems-therapy-history/check_pack.py` | **PASS** (44 articles, 0 errors) |
| `voice_check` on every article | **`edited`** (read-aloud + tighten pass) |
| Banned phrase scan | Clean (automated) |
| Educational note on every article | Present |
| Era ≥1,200 / figure ≥1,000 words | Met after edits |

Log: `/opt/cursor/artifacts/family_systems_pack_check.log`

## What changed in this pass

### Voice and structure (substantive)

Seven **living-writer** figure essays had stacked staccato recap sections (word-count padding from the writer draft). Those blocks repeated catalogue discipline, portrait rules, and neighbor lists three or four times. This pass:

- **Removed** duplicate recap headings while keeping dated bibliography sections.
- **Replaced** repetition with single, readable sections (still history-only; no how-tos).
- **Re-expanded** where consolidation dropped a figure below the 1,000-word floor.

| Article | Editor action |
| --- | --- |
| `34-monica-mcgoldrick.md` | Dropped redundant "week fourteen" recap; kept later-editions spine. |
| `33-david-epston.md` | Consolidated Auckland/letter/Māori ethics into one section; added witness/audience paragraph. |
| `39-celia-jaes-falicov.md` | Consolidated MECA/migration recaps; added Guilford 1998 context section. |
| `41-harry-aponte.md` | Merged 1994/managed-care staccato; added faith/poverty section. |
| `37-sue-johnson.md` | Merged Ottawa/EFT recaps; added attachment-loop / diagram-hides-bruise section. |
| `40-pauline-boss.md` | Merged 1999/Harvard recaps; added neighbors-on-shelf section. |
| `44-kenneth-hardy.md` | Merged catalogue/present-tense recaps; kept 2005/2016 book spine. |
| `29-paul-watzlawick.md` | Merged duplicate Jung/MRI staccato into one dated close. |

### Full pack (read-aloud)

Remaining **36** era and figure essays: read against `STYLE_GUIDE.md` and `CLAIMS_GUARDRAILS.md`. No banned phrases found. Protocol refusals (genogram blanks, miracle questions, race-dialogue lists, rituals, hold-me-tight exercises) left explicit where the writer already had them. `voice_check` set to **`edited`** on all 44.

### Unchanged on purpose

- **`[VERIFY]`** markers on living-writer birth years and vital dates (Boss, Johnson, Epston, Aponte, Madanes, etc.) — hold for authority-file check before live print per `CLAIMS_GUARDRAILS.md`.
- **`status: draft`** — staging only; import per `WP_IMPORT.md`.
- **Portraits:** `portrait: none` / type-only discipline unchanged.
- **Schizophrenogenic / family-causes-schizophrenia:** still named as mid-century injury, not fact (era essay 03 and cross-refs).

## Protocol / claims audit (manual)

Spot-checked all articles for:

- Session scripts, worksheets, genogram how-tos, miracle/circular-question teaching  
- DIY "try at home" or self-treat language  
- Gold-standard treatment marketing  
- WOW Therapies service claims on history URLs  

**Finding:** Refusals and footers are in place. Named methods appear as **dated historical objects** only. No new protocol content introduced in this pass.

## Ops files touched

| File | Change |
| --- | --- |
| `EDITOR_REPORT.md` | This report (new) |
| `MANIFEST.md` | Inventory row for editor report |
| `README.md` | Pointer to editor report |
| `articles/*.md` | Editorial body edits (8 files) + `voice_check: edited` (44 files) |

## Recommended before live site

1. Resolve `[VERIFY]` birth/vital dates against library or publisher authority files.  
2. Portrait upload day: only objects in `PORTRAIT_SOURCES.md` (Bell 1961 GPO, Healy 1915 title page).  
3. Human sign-off on living-writer paragraphs after any catalogue update.  
4. Import staging only; do not map `draft` to production publish without a second review.

## Editor sign-off

Educational heritage lane only. No treatment protocols. Pack QA green. Ready for continued **draft** PR review — not for merge to live WOWTherapies without staging import and verify cleanup.
