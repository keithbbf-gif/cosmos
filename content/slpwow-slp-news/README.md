# SLP News — SLPWOW draft pack

Staged originals for [SLP News](https://slpwow.com/blog/) on slpwow.com. **Draft only.** Nothing here is cleared to go live.

- `articles/` — 46 markdown features and briefs
- `INDEX.md` — inventory, slugs, word counts
- `BIBLIOGRAPHY.md` — all cited public sources
- `WP_IMPORT.md` — WordPress **Draft** import only
- `CLAIMS_GUARDRAILS.md` — no diagnosis, no PHI, no invented quotes
- `EDITOR_REPORT.md` — editor sign-off for the current pass (`voice_check: edited`)
- `check_slp_news.py` — pack QA (claims fence, brochure voice, frontmatter)
- `_SOURCE_PACK.md` / `_TEMPLATE.md` — desk-internal; do not import as posts

## Editor QA

```bash
python3 content/slpwow-slp-news/check_slp_news.py
python3 -m pytest tests/test_slpwow_slp_news.py -q
```

Every file in `articles/` must carry `voice_check: edited` after review.

Existing live posts that this pack updates rather than clones:

- [ASLP-IC Expands](https://slpwow.com/2025/01/30/aslp-ic-expands/) (Jan 2025, 35 members; privileges not yet issuing)
- [ASHA Analyzes the 2025 Medicare Fee Schedule](https://slpwow.com/2025/01/18/asha-analyzes-the-2025-medicare-fee-schedule-for-audiologists-and-slps/)

Desk date for this pack: 14 September 2026.
