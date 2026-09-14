# WordPress import — draft only

This pack is staged writing. Nothing here is cleared to go live.

## Rule

Import every essay as a WordPress **draft**. Do not publish, schedule, or ping a sitemap from this folder. An editor pass still has to run. Photo files still have to be pulled from `D:\BBF\BBF Photos` (or a later owner path) and credited from metadata, not from these notes.

## Suggested mapping

| Pack field | WordPress |
|---|---|
| `title` | Post title |
| `dek` | Excerpt |
| `slug` | Post slug (keep) |
| `status: draft` | `draft` — do not override |
| `topic` | Category or a single craft tag |
| `series: furniture-craft` | Tag `furniture-craft` |
| `figures` | Media library items, attached after files exist |
| `optional_links` | Optional footnote block, not the first paragraph |
| body after front matter | Post content (Markdown → block editor or a Markdown importer) |

## Import methods (pick one later)

1. **Manual.** One draft post at a time. Safest. Matches the tone of this pack.
2. **WP-CLI.** `wp post create --post_type=post --post_status=draft --post_title=... --post_excerpt=... --post_name=slug --post_content=...`  
   Keep `--post_status=draft`.
3. **WXR / CSV.** Only if an editor builds the file from this folder. The XML/CSV itself should set `<wp:status>draft</wp:status>` or the CSV equivalent. Do not generate a “publish” column here.

Do not auto-set a featured image until the shop-library file is in hand. A missing photo is better than a stock-image stand-in.

## Categories (suggested, not required)

- Joinery
- Tools
- Finish
- Materials
- Millwork
- Shop
- Culture
- Repair

One category per post is enough. Tags can carry wood species and joint names.

## What not to do

- Do not paste brand URLs into every excerpt.
- Do not set Yoast/RankMath focus keys from this pack.
- Do not syndicate to a shop feed until the editor signs the voice.
- Do not upload historical postcards until rights are cleared (`[VERIFY rights]` in `PHOTO_CAPTIONS.md`).

## After import

Leave posts in Draft. The editor agent (or a human) owns grammar, house spelling, and the last cut. Publication is a later verb.
