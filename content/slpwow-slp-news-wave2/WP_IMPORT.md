# WordPress import notes — wave 2

Staged markdown only. This pack does **not** write the live SLPWOW CMS.

## Suggested WP mapping

| YAML | WP |
| --- | --- |
| `title` | Post title |
| `slug` | Post slug (`/slp-news/{slug}/`) |
| `meta_description` | Yoast / excerpt |
| `desk` | Category: ASHA, CMS, Compact, Research, Literacy |
| `tags` | Post tags |
| `citations` | Footer “Sources” (already in body) |
| `status: draft` | WP draft. Do not publish from this folder. |

## Series

Parent series: SLP News. Wave 1 posts stay in their own category. Wave 2 slugs must not collide with `content/slpwow-slp-news/articles/`.

## Do not import

- `check_pack.py`
- editorial markdown in this folder root (including `EDITOR_REPORT.md`)
- `BIBLIOGRAPHY.md` as a public post (staff page only, if at all)

## Before publish

Re-hit any body line marked **`[VERIFY]`** (Compact Map counts, live Commission legends). Re-open CMS Therapy Services and the CY 2026 fact sheet before printing KX or conversion-factor dollars in a handout.
