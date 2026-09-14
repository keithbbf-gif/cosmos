# WordPress import — draft only

This pack is staged writing. Nothing here is cleared to go live.

## Rule

Import every essay as a WordPress **draft**. Do not publish, schedule, or ping a sitemap from this folder. An editor pass still has to run. Photo files still have to be pulled from museum URLs (with license) or from `D:\BBF\BBF Photos` and credited from metadata, not from these notes.

## Suggested mapping

| Pack field | WordPress |
|---|---|
| `title` | Post title |
| `dek` | Excerpt |
| `slug` | Post slug (keep) |
| `status: draft` | `draft` — do not override |
| `topic` | Category or a single chair tag |
| `series: dining-chairs-history-design` | Tag `dining-chairs` |
| `primary_keyword` | SEO plugin focus key — set later, not at import |
| `figures` | Media library items, attached after files exist |
| `optional_links` | Optional footnote block, not the first paragraph |
| body after front matter | Post content |

## Import methods (pick one later)

1. **Manual.** One draft post at a time. Safest.
2. **WP-CLI.** `wp post create --post_type=post --post_status=draft ...` — keep `--post_status=draft`.
3. **WXR / CSV.** Only if an editor builds the file from this folder. Status must stay draft.

Do not auto-set a featured image until the file is in hand. A missing photo is better than a stock-image stand-in.

## Categories (suggested)

- History
- Form
- Ergonomics
- Materials
- Shop
- Culture
- Labor

One category per post is enough.

## What not to do

- Do not paste brand URLs into every excerpt.
- Do not set Yoast/RankMath focus keys from this pack on import day.
- Do not syndicate to a shop feed until the editor signs the voice.
- Do not upload historical postcards until rights are cleared.
- Do not title an ergonomics post as if BIFMA certified a dining chair.

## After import

Leave posts in Draft. Publication is a later verb.
