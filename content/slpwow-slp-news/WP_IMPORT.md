# WordPress import — Draft only

This pack is **staged**. Every article is `status: draft` and `category: slp-news`. **Do not Publish. Do not schedule. Do not send to the live SLP News index.**

Target site: [https://slpwow.com/blog/](https://slpwow.com/blog/) (titled **SLP News**).

## What to import

Import **only** files in `articles/*.md`.

Do **not** create posts from:

- `README.md`
- `INDEX.md`
- `BIBLIOGRAPHY.md`
- `CLAIMS_GUARDRAILS.md`
- `_SOURCE_PACK.md`
- `_TEMPLATE.md`
- this file

## Status and taxonomy

| Field | WordPress |
|---|---|
| `status: draft` | Post status = **Draft** (never Publish) |
| `category: slp-news` | Category **SLP News** (create if missing; slug `slp-news`) |
| `article_type` | Optional custom field `article_type` = `feature` or `brief` |
| `slug` | Post slug (permalink) |
| `title` | Post title |
| `dek` | Excerpt / standfirst |
| `dateline` + first paragraph | Keep in body; do not strip the dateline |
| `story_date` | Post date (draft dates may stay in the past; do not auto-set “now” as publish) |
| `author: SLP News desk` | Map to the existing SLP News / Wigley / Addy byline the editor chooses |
| `sources` YAML + `## Sources` | Keep the body Sources list. Optionally paste YAML into a custom field `source_urls` |
| `notes` | Internal only — do not display |

## Recommended editor path (no plugin required)

1. WordPress Admin → Posts → Add New.
2. Paste **title**, then body from `# Headline` downward (omit the YAML fence).
3. Set **Excerpt** to `dek`.
4. Set category **SLP News**.
5. In Document → Status, choose **Draft**. Save. Do not click Publish.
6. Permalink → slug from front matter.
7. Repeat. Suggested waves so the live site never sees a partial dump:
   - Wave A (compact): `01`–`11`
   - Wave B (Medicare): `12`–`23`
   - Wave C (workforce): `24`–`33`
   - Wave D (research + practice): `34`–`46`

If a Markdown importer is used (WP All Import, WP-CLI `wp post generate`, etc.), force `post_status=draft` in the mapping. A default of `publish` is a failed import.

## House style on paste

- Keep the disclaimer sentence: *This article does not offer clinical advice, billing guarantees, or diagnosis guidance.*
- Keep source URLs. Do not strip them for “clean look.”
- Do not paste ASHA fee tables from the public PDF even if an editor later opens that PDF.
- Do not add stock “clinicians say” pull quotes.
- Recheck Compact Map and CMS Therapy Services the week any piece is considered for Publish. This pack’s facts are dated 14 September 2026.

## Existing live posts

These 2025 SLP News items stay up. New drafts **update** those stories; they do not replace them automatically.

- https://slpwow.com/2025/01/30/aslp-ic-expands/
- https://slpwow.com/2025/01/18/asha-analyzes-the-2025-medicare-fee-schedule-for-audiologists-and-slps/

Link from the new compact/Medicare drafts to those URLs if the editor wants a “previously on SLP News” line. Do not overwrite the old posts in place.

## Import checklist (per post)

- [ ] Status is Draft
- [ ] Category is SLP News
- [ ] Slug matches front matter
- [ ] Sources list present
- [ ] Disclaimer present
- [ ] No featured image scraped from a journal PDF
- [ ] No “Publish” click
