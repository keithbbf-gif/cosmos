---
pack: slpwow-slp-news
doc: EDITOR_REPORT
status: news-drafts-wave-1
voice: newsroom
voice_check: edited
lint: check-slp-news
---

# Editor report — `slpwow-slp-news`

**Pull request:** [#453](https://github.com/keithbbf-gif/cosmos/pull/453)  
**Editor pass:** 2026-09-14 (UTC)  
**Scope:** 46 `articles/*.md` drafts, pack README/guardrails, `check_slp_news.py`, pytest gate  
**Outcome:** `voice_check: edited` on every article; claims-fence and newsroom voice verified; two lede-line tightenings. **Draft PR only — not merged.**

## Mandate

Quality over speed. Newsroom voice per `CLAIMS_GUARDRAILS.md`: primary sources, enacted vs issuing vs final, no diagnosis or billing guarantees, no fabricated or composite quotes, no brochure filler.

## Method

1. Read `CLAIMS_GUARDRAILS.md`, `INDEX.md`, `WP_IMPORT.md`, and spot-read features across ASLP-IC, Medicare/CMS, school workforce, and research beats.
2. Grep sweeps for brochure terms, composite attribution (`clinicians say`), and billing-guarantee phrasing.
3. Confirm every feature carries a claims-fence block (`What this is not`, `What SLPs should verify`, or brief-equivalent `did not add` / `is not` sections).
4. Add `voice_check: edited` to all article frontmatter.
5. `python3 content/slpwow-slp-news/check_slp_news.py`
6. `python3 -m pytest tests/test_slpwow_slp_news.py -q`

## Narrative edits

| File | Change | Rationale |
| --- | --- | --- |
| `articles/33-rhode-island-even-year-renewal.md` | “before you write a check” → “before paying a renewal fee” | Keeps statute summary in desk voice; verification stays in RIDOH links, not second-person aside. |
| `articles/11-commission-newsletters-are-the-record.md` | “before you quote” → “before quoting” | Same: procedural guidance without shifting into advice-column “you.” |

No headline, slug, source URL, or dollar-figure changes. `What SLPs should verify` sections keep directed verification language by design (guardrails: verify, not treat).

## Furniture / tooling

- **`voice_check: edited`** on all 46 articles in `articles/`.
- **`check_slp_news.py`** — frontmatter, disclaimer sentence, `## Sources`, feature claims-fence, slug uniqueness, brochure/composite/billing-guarantee scans.
- **`tests/test_slpwow_slp_news.py`** — CI gate on the checker.
- **`README.md` / `CLAIMS_GUARDRAILS.md` / `_TEMPLATE.md`** — document the `voice_check` contract and QA commands.

## Verification

```
PASS  slpwow-slp-news  articles=46  slugs=46
pytest: passed
```

## Sign-off

| Field | Value |
| --- | --- |
| `voice_check` | `edited` (all articles) |
| `check_slp_news` | pass |
| `pytest` | pass |
| Merge | **no** — draft PR #453 only |
