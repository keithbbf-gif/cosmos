# Editor report — SLPWOW SLP News (practice wave)

**Pass date:** 2026-09-14  
**Branch:** `cursor/slpwow-slp-news-practice-editor-a4de` (stacked on `cursor/slpwow-slp-news-practice-d70b`, writer PR #467)  
**Editor:** Cloud agent (EDITOR role)  
**Scope:** `content/slpwow-slp-news-practice/` only — news explainers, not protocols

## Verdict: proceed (not a stub pack)

| Check | Result |
|-------|--------|
| Articles in `articles/` | 46 |
| Stub / placeholder bodies | **0** — no shared boilerplate, no “coming soon,” no empty sections |
| Body word count range | ~652–1,070 words per file (~33.6k total) |
| Pieces under 650 words | **0** (shortest: `14-mppr-same-day-math.md` at 652) |
| `check_pack.py` | **OK** (46 drafts) |
| Style-guide slop grep | **0** hits (`delve`, `leverage`, `robust`, `game-changer`, `whether you're`, etc.) |
| Banned billing / protocol script grep | **0** hits (`bill 92507`, `always append KX`, `try this protocol`, `home program:`) |
| `[CITE NEEDED]` in bodies | **0** |
| `[VERIFY]` on printed dollars | **0** — flags only on live-URL / AAP-PDF caveats at publish time |

**HOLD not issued.** The writer pack is full magazine copy with consistent disclaimers, named public sources, and explicit “this page will not print…” boundaries.

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed (full read + pack scan) | 46 |
| Drafts updated (`voice_check: edited`) | 46 |
| Targeted prose / heading clarifications (news vs protocol) | 4 |
| Pack metadata files updated | 5 (`INDEX.md`, `MANIFEST.md`, `WP_IMPORT.md`, `check_pack.py`, this report) |

## What was fixed

1. **Front matter** — Replaced `voice_check: human` with `voice_check: edited` and added `voice_check_date: 2026-09-14` on every article.
2. **News-not-protocols pass** — Clarified numbered “habit” sections so they cannot be mistaken for clinical or billing worksheets:
   - `articles/02-abstracts-are-not-the-study.md` — section title now names a *reading habit*, not a protocol.
   - `articles/05-when-a-review-is-just-a-list.md` — four staff-meeting questions framed as *reading discipline*, not a house protocol.
   - `articles/16-targeted-medical-review-three-thousand.md` — KX / MR stack labeled *policy map*, not a claim script.
3. **Smoke check** — `check_pack.py` now validates `voice_check` is `human` or `edited`.
4. **Preserved** — Dollar figures tied to CY 2026 CMS / ASHA public pages; reimbursement pieces still refuse minute charts, NCCI modifier recipes, and ABN tick-box scripts; practice-headline pieces still refuse maneuver lists, IDDSI test cards, LSVT homework, and AAC implementation calendars.

## Voice notes (no wholesale rewrite required)

- Openings are mailbox-, PDF-, or hallway-led; CEU-mill tone is absent.
- Repeated “It is not…” / “This page will not…” blocks are intentional guardrails (inverse of protocol dumps), not filler.
- Research-literacy numbered lists (02, 05) teach *how to read mail*; they do not prescribe treatment steps.
- Cross-essay pointers (“essay 15”) build a serial magazine; left intact.

## Remaining weak spots (for writer, coder, or publish gate)

| Area | Note |
|------|------|
| Short reimbursement briefs | 14, 20, 22, 28 sit near the 650-word floor but pass; do not pad — add only if a transmittal changes. |
| `[VERIFY]` at publish | Essays 41, 44, 46 flag live CDC/NIDCD/AAP/ACS URLs — re-hit before any URL goes public. |
| Teacher voice % | `39-teacher-voice-occupational-news.md` and `BIBLIOGRAPHY.md` defer a specific prevalence % to the paper you hold. |
| Graphics | No figure pipeline in this pack; headlines are text-only. |
| Licensed sign-off | `WP_IMPORT.md` still requires a licensed SLP + editor before staging import. |

## Articles flagged for extra care (already honest in copy)

| Slug | Note |
|------|------|
| `thickened-liquids-the-research-keeps-getting-reread` | Holds instrumental vs outcome tension without a diet order. |
| `when-the-school-reads-a-swallow-study` | School vs medical orders; no classroom VFSS repeat. |
| `voice-and-the-ppi-story` | PPI hoarseness guideline; no prescribe/discontinue script. |
| `eight-minute-rule-is-news` | Refuses the minute-to-unit table on purpose. |
| `iddsi-version-news` | Refuses IDDSI test-card reprints. |

## Not in scope

- No WordPress publish actions.
- No COSMOS core / live tree paths.
- No merge of writer PR #467 (editor PR stays draft until human review).

## Verification commands (reproducible)

```bash
python3 content/slpwow-slp-news-practice/check_pack.py
rg -c 'voice_check: edited' content/slpwow-slp-news-practice/articles | wc -l   # expect 46
rg 'voice_check: human' content/slpwow-slp-news-practice/articles || true
rg -i 'delve|leverage|robust|game-?changer|whether you.re' content/slpwow-slp-news-practice/articles || true
```
