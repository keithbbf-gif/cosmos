# Editor report — SLPWOW school caseload / practice / news

**Pass date:** 2026-09-14  
**Branch:** `cursor/slp-school-caseload-practice-news-editor-9f18` (stacked on `cursor/slp-school-caseload-practice-news-2eab`, writer PR #501)  
**Editor:** Cloud agent (EDITOR role)  
**Scope:** `content/slp-school-caseload-practice-news/` only — educational explainers, not protocols

## Verdict: proceed (not a stub pack)

| Check | Result |
|-------|--------|
| Articles in `articles/` | 44 |
| Stub / placeholder bodies | **0** — no shared boilerplate, no “coming soon,” no empty sections |
| Body word count range | ~650–1,070 words per file (~31.4k total) |
| Pieces under 650 words | **0** (shortest: `40-ai-for-ieps-what-the-news-is-about.md` at 650) |
| `check_pack.py` | **OK** (44 drafts) |
| Style-guide slop grep | **0** hits (`delve`, `leverage`, `robust`, `game-changer`, `whether you're a`, etc.) |
| Banned PHI / cap / diagnosis script grep | **0** hits in bodies |
| Billing codes in bodies | **0** — essay 32 names CPT only to refuse codes |
| `[CITE NEEDED]` in bodies | **0** |
| `[VERIFY]` | Present only on publish-time caveats (ASHA AI page, state statute, Marante cite, preschool figure, §300.154 text) — not on printed 2024 survey medians |

**HOLD not issued.** The writer pack is full magazine copy with consistent disclaimers, named public sources, and explicit “this page will not…” boundaries.

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed (full read + pack scan) | 44 |
| Drafts updated (`voice_check: edited`) | 44 |
| Targeted prose / heading clarifications (practice vs protocol) | 3 articles |
| Pack metadata files updated | 4 (`MANIFEST.md`, `WP_IMPORT.md`, `EDITOR_REPORT.md`, this report) |

## What was fixed

1. **Front matter** — Replaced `voice_check: human` with `voice_check: edited` and added `voice_check_date: 2026-09-14` on every article.
2. **Practice-not-protocol pass** — Clarified numbered / page sections so they cannot be mistaken for clinical worksheets:
   - `articles/22-present-levels-a-teacher-can-use.md` — colleague check framed as a drafting habit, not a standardized test or treatment step.
   - `articles/27-group-composition-without-stacking.md` — “Five hallway tells” labeled as stacking reads, not a group-therapy protocol.
   - `articles/43-briefing-a-principal-on-workload.md` — three-page principal brief labeled as an outline, not a photocopy worksheet or union script; page headings marked `(outline)`.
3. **Preserved** — 2024 ASHA medians (50 / 40) with n; refusal of a national cap; essay 24’s critique of “30 × 2” as habit, not prescription; essay 32’s refusal of CPT/units; no named students; no treatment maneuvers.

## Voice notes (no wholesale rewrite required)

- Openings are headline-, PDF-, or hallway-led; vendor cheerleading is absent.
- Repeated “You can refuse…” closers are intentional guardrails, not filler.
- Cross-essay pointers (“essay 07”) build a serial magazine; left intact.
- `whether you` appears only in ordinary prose (“whether you want them to”), not the banned “whether you’re a parent or clinician” opener.

## Remaining weak spots (for writer, coder, or publish gate)

| Area | Note |
|------|------|
| Floor-length pieces | 40, 35, 19, 21, 38, 39, 43 sit at 650–653 words; pass checker — do not pad without a factual add. |
| `[VERIFY]` at publish | Essays 09, 32, 37, 40 (and preschool figures in 04) flag live URLs or moving ASHA pages — re-hit before public URLs. |
| Graphics | No figure pipeline in this pack; headlines are text-only. |
| Licensed sign-off | `WP_IMPORT.md` still requires a licensed SLP + editor before staging import. |

## Articles flagged for extra care (already honest in copy)

| Slug | Note |
|------|------|
| `medicaid-in-schools-without-billing-advice` | Federal guide + consent doors; refuses coding. |
| `minutes-frequency-and-lre` | Names “30 × 2” only to refuse it as a default. |
| `ai-for-ieps-what-the-news-is-about` | FERPA / PTAC boundary; no student text in public models. |
| `union-salary-schedule-and-retention` | Describes retention data; refuses strike / vote advice. |
| `autism-on-the-caseload-educational` | Educational service pattern only; no label for a child. |

## Not in scope

- No WordPress publish actions.
- No COSMOS core / live tree paths.
- No merge of writer PR #501 (editor PR stays **draft** until human review).

## Verification commands (reproducible)

```bash
python3 content/slp-school-caseload-practice-news/check_pack.py
rg -c 'voice_check: edited' content/slp-school-caseload-practice-news/articles | wc -l   # expect 44
rg -i 'delve|leverage|robust|game-changer|whether you''re a' content/slp-school-caseload-practice-news/articles || true
```
