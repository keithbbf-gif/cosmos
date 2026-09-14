# Editor report — SLPWOW SLP News, wave 2

**Pass date:** 2026-09-14  
**Branch:** `cursor/slpwow-slp-news-wave2-editor-f486` (stacked on `cursor/slpwow-slp-news-wave2-8fbb`, writer PR #493)  
**Editor:** Cloud agent (EDITOR role)  
**Scope:** `content/slpwow-slp-news-wave2/` only — public-document news briefs, not protocols

## Verdict: proceed (not a stub pack)

| Check | Result |
|-------|--------|
| Articles in `articles/` | 46 |
| Stub / placeholder bodies | **0** — no shared boilerplate, no “coming soon,” no empty sections |
| Body word count range | ~520–900 words per file (~28k total) |
| Pieces under 520 words | **0** (`check_pack.py` floor) |
| `check_pack.py` | **OK** (46 drafts) |
| Style-guide slop grep | **0** hits (`delve`, `leverage`, `robust`, `game-changer`, `whether you're`, etc.) |
| `[CITE NEEDED]` in bodies | **0** |
| `[VERIFY]` on CY 2026 CMS/ASHA fee dollars | **0** — $2,480 KX, $33.40/$33.57 CF tied to cited CMS/MM/ASHA PDF pages |
| `[VERIFY]` on live Compact Map counts | **Yes** — articles `12`, `30` (legend numerators + issuing names) |

**HOLD not issued.** Writer pack is full magazine copy with consistent disclaimers, named public sources, and explicit “this page will not print…” boundaries.

## Summary

| Metric | Count |
|--------|------:|
| Drafts reviewed (pack scan + literacy desk full read; spot read on CMS/compact/research) | 46 |
| Drafts updated (`voice_check: edited`) | 46 |
| Targeted prose / news-literacy clarifications | 4 |
| Pack metadata files updated | 7 (`INDEX` unchanged roster; `MANIFEST.md`, `WP_IMPORT.md`, `CLAIMS_GUARDRAILS.md`, `STYLE_GUIDE.md`, `check_pack.py`, this report) |

## What was fixed

1. **Front matter** — Replaced `voice_check: human` with `voice_check: edited` and added `voice_check_date: 2026-09-14` on every article.
2. **News literacy (desk 01)** — Clarified which 2026 numbers are URL-locked vs map-locked; replaced editorial “we will not” with “this desk will not” to match the no-corporate-we rule.
3. **`[VERIFY]` discipline** — Tagged volatile Compact Map legend counts in `12-workforce-is-an-access-story.md` and `30-thirty-seven-and-four.md`. Left CY 2026 Medicare dollars untagged where MM14315, the Therapy Services page, or CMS-1832-F is the cited primary.
4. **Voice consistency** — `22-targeted-manual-review.md` “We will not publish…” block aligned to desk voice.
5. **Smoke check** — `check_pack.py` now accepts `voice_check` `human` or `edited`.
6. **Import gate** — `WP_IMPORT.md` and `CLAIMS_GUARDRAILS.md` document re-hit rules for `[VERIFY]` and CMS dollars.

## Voice notes (no wholesale rewrite required)

- Openings stay document- or date-led; CEU-mill tone is absent.
- Repeated “It is not…” / “This page will not…” blocks are intentional guardrails, not filler.
- Literacy essay 01 is the routing card for wave 2; cross-refs to later brief numbers left intact.
- Research desk pieces (CATALISE, CDC 75%, IDDSI, telepractice reviews) already separate surveillance from diagnosis; not rewritten.

## Remaining weak spots (for writer, coder, or publish gate)

| Area | Note |
|------|------|
| Short CMS briefs | Several pieces sit near the 520-word floor; do not pad — add only if a transmittal changes. |
| `[VERIFY]` at publish | Compact Map numerators in essays 12 and 30; re-open `aslpcompact.com/compact-map/` before any public URL. |
| CDC / Act Early URLs | Essay 39 — confirm live CDC paths before print (CDC moves paths). |
| DOI papers | Essays 41, 43–46 — open-access links stable in bibliography; paywall abstracts still not pasted. |
| Graphics | No figure pipeline in this pack; wave 1 holds SVG cards. |
| Licensed sign-off | `WP_IMPORT.md` still requires licensed SLP + human editor before staging import. |

## Articles flagged for extra care (already honest in copy)

| Slug | Note |
|------|------|
| `thirty-seven-and-four` | Teaches enacted vs issuing ratio; `[VERIFY]` on map counts. |
| `kx-is-2480-combined` | PT+SLP shared bucket; refuses “cap is back” language. |
| `asha-reads-the-2026-fee-schedule` | Booklet vs rule; telehealth date overtaken by statute — already noted. |
| `cdc-75-percent-milestones` | Surveillance vs screen vs eval; not ASHA’s list. |
| `iddsi-is-not-a-cms-diet` | No thickener recipes; PDPM flags ≠ IDDSI audit. |

## Not in scope

- No WordPress publish actions.
- No COSMOS core / live tree paths.
- No merge of writer PR #493 (editor PR stays **draft** until human review).

## Verification commands (reproducible)

```bash
python3 content/slpwow-slp-news-wave2/check_pack.py
rg -c 'voice_check: edited' content/slpwow-slp-news-wave2/articles | wc -l   # expect 46
rg 'voice_check: human' content/slpwow-slp-news-wave2/articles || true
rg '\[VERIFY\]' content/slpwow-slp-news-wave2/articles
rg -i 'delve|leverage|robust|game-?changer|whether you.re' content/slpwow-slp-news-wave2/articles || true
```
