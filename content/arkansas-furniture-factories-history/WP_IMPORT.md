# WordPress import — draft only

This pack is staged writing. Nothing here is cleared to go live.

## Rule

Import every essay as a WordPress **draft**. Do not publish, schedule, or ping a sitemap from this folder. An editor pass still has to run. Photo files still have to be pulled from `D:\BBF\BBF Photos` (or a later owner path) and credited from metadata, not from these notes. Archive frames from the Fort Smith Museum of History, NWS, or newspapers need **rights** before they become media library items.

## Suggested mapping

| Pack field | WordPress |
|---|---|
| `title` | Post title |
| `dek` | Excerpt |
| `slug` | Post slug (keep) |
| `status: draft` | `draft` — do not override |
| `topic` | Category (`origins`, `fort-smith-companies`, `riverside`, `wood-and-rail`, `labor-civic`, `statewide`, `afterlife`) |
| `series: arkansas-furniture-factories-history` | Tag `arkansas-furniture-factories-history` |
| `figures` | Shop / documentary photos (`D:\BBF`) — attach after files exist |
| `optional_links` | Optional footnote block, not the first paragraph |
| body after front matter | Post content (Markdown → block editor or a Markdown importer) |
| `<!-- PHOTO: fig-0N … -->` | Pull instruction — replace with the media item once the file exists |

## Import methods (pick one later)

1. **Manual.** One draft post at a time. Safest.
2. **WP-CLI.** `wp post create --post_type=post --post_status=draft …` — keep `--post_status=draft`.
3. **WXR / CSV.** Only if an editor builds the file from this folder. The XML/CSV itself should set `<wp:status>draft</wp:status>`. Do not generate a “publish” column here.

Do not auto-set a featured image until the library file is in hand. A missing photo is better than a stock-image stand-in. Do not set Yoast/RankMath focus keys from this pack.

## What not to do

- Do not paste brand URLs into every excerpt.
- Do not syndicate until the editor signs the voice.
- Do not treat this pack as a retread of `content/arkansas-southern-woods-species/` or the joinery pack.
- Do not claim Bradley Brand Furniture as the successor of Bradley Lumber Company, Ballman-Cummings, or Riverside.

## After import

Leave posts in Draft. Publication is a later verb.
