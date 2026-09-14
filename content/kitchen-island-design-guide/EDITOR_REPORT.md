# Editor report — kitchen island design guide

**Branch:** `cursor/kitchen-island-design-guide-editor-fabe` (editor PR stacked on writer `cursor/kitchen-island-design-guide-45c2`, PR **#301**)  
**Editor pass date:** 2026-09-14  
**Scope:** `content/kitchen-island-design-guide/` — README, MANIFEST, 48 drafts under `drafts/`

## Remediation

- **Do not merge** this PR until writer **#301** is reviewed; editor PR targets the writer branch, not `main`.
- Preserve staged status: `status: staged` unchanged on all drafts.

## Scope completed

| Item | Result |
| --- | --- |
| Drafts line-edited | **48/48** |
| `voice_check: edited` | **48/48** (enforced in `tools/check_island_drafts.py`) |
| Structure (stages, ids, slugs, topics) | Unchanged |
| AI slop grep (`check_island_drafts.py` SLOP list) | **0 hits** before and after |
| Automated QA | `python3 tools/check_island_drafts.py` → **OK** |

Post-pass metrics: **18,987 words** (min **352**, max **520** on sequence draft 47 after cross-ref expansion).

## Edit themes

1. **Voice:** Kept designer-on-the-floor monologue; trimmed meta (“next pass” in 01); replaced “loophole” / “argument to end” phrasing that read like marketing or code cynicism (43, 24).
2. **Grammar / units:** Fixed `1999 NEC energy` → `era` (07); `a honest` → `an honest` (22); NKBA dimension shorthand (`36 by 24`, `16 deep`, knee space inches) clarified in 06, 10, 11.
3. **Electrical accuracy tone:** 210.52(C)(3) 20 in. wording aligned in 35; GFCI voltage range hyphenation in 40; CMP-2 injury narrative tied to `[VERIFY]` in 07 and 37 (no unsourced “thousands” without flag).
4. **Cross-refs:** Sequence draft 47 now cites piece titles plus id numbers instead of bare “Draft N” labels.
5. **Bradley / code facts:** `[VERIFY]` added where copy depends on dealer book or local adoption (02 build geography, 44 box spec, 15 makeup-air threshold, NEC stats).

## Files with substantive body edits

| id | File | Notable change |
| --- | --- | --- |
| 01 | `01-why-this-guide.md` | Brochure meta → human QA instruction |
| 02 | `02-what-bradley-island-means.md` | U.S./Canada build `[VERIFY]` |
| 06 | `06-work-triangle-to-work-zones.md` | Prep zone dimensions in inches |
| 07 | `07-islands-that-failed.md` | NEC era typo; CMP-2 injury `[VERIFY]` |
| 10 | `10-minimum-useful-island.md` | Landing depth units |
| 11 | `11-three-heights.md` | Knee-space units |
| 15 | `15-landing-zones.md` | Makeup-air cfm → code threshold `[VERIFY]` |
| 22 | `22-wood-moves.md` | Article agreement |
| 24 | `24-quartz-low-drama.md` | Opening voice |
| 35 | `35-two-tier-islands.md` | NEC 210.52(C)(3) location wording |
| 37 | `37-what-2023-nec-changed.md` | Deduped injury paragraph; `[VERIFY]` |
| 40 | `40-gfci-the-whole-kitchen.md` | Voltage range typography |
| 43 | `43-usb-and-what-belongs-below.md` | USB allowance tone |
| 44 | `44-full-access-frameless-boxes.md` | Dealer book `[VERIFY]` |
| 47 | `47-sequence-measure-to-stools.md` | Title-based cross-refs |

Drafts **03–05, 08–09, 12–14, 16–21, 23, 25–34, 36, 38–39, 41–42, 45–46, 48** received `voice_check: edited` plus light punctuation/consistency only (no fact changes).

## `[VERIFY]` checklist (human / counsel before publish)

- NEC **edition adopted locally** and text of 210.52(C)(2), (C)(3), 210.8(A)(6), (D) vs drafts 37–41, 43.
- **CMP-2 / NFPA** injury statistics cited for 2023 island receptacle changes (07, 37).
- **NKBA** aisle, triangle, landing, seating, and access numbers paraphrased in proportions drafts.
- **Bradley dealer book:** build geography, 3/4 in. box spec, baseline hardware claims (02, 44, 46).
- **Mechanical / hood** makeup-air threshold for high-cfm hoods (15).
- **Fabricator shop numbers** for stone/wood overhang and weight (01 disclaimer still governs).

## Tooling

- `tools/check_island_drafts.py`: requires `voice_check: edited` in frontmatter.

## Sign-off

Editor agent: **pass** for grammar, voice, slop ban, and checker gates. Ready for design/electrical partner review on stacked editor PR (writer **#301**).
