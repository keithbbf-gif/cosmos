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
| `topic` | Category (`dating-trade`, `the-box`, `case-and-fit`, `tradition-hardware`) |
| `series: drawer-construction-history` | Tag `drawer-construction-history` |
| `figures` | **Shop photos** (`D:\BBF`) — media library items, attached after files exist; stay `needed` until pull |
| `graphics` | **Figure 1 schematics** — CC0 SVG in `assets/<slug>/`; see `RIGHTS.md` |
| body `<figure class="dch-figure">` | Staged HTML for import — see `SEO_MAP.md` |
| `optional_links` | Optional footnote block, not the first paragraph |
| body after front matter | Post content (Markdown → block editor or a Markdown importer) |
| `<!-- PHOTO: fig-0N … -->` | Pull instruction — replace with the media item once the file exists |

## Import methods (pick one later)

1. **Manual.** One draft post at a time. Safest.
2. **WP-CLI.** `wp post create --post_type=post --post_status=draft …` — keep `--post_status=draft`.
3. **WXR / CSV.** Only if an editor builds the file from this folder. The XML/CSV itself should set `<wp:status>draft</wp:status>`. Do not generate a “publish” column here.

Do not auto-set a featured image until the shop-library file is in hand. A missing photo is better than a stock-image stand-in.

## What not to do

- Do not paste brand URLs into every excerpt.
- Do not set Yoast/RankMath focus keys from this pack.
- Do not syndicate until the editor signs the voice.
- Do not treat this pack as a retread of `content/furniture-craft-blog/` or `content/furniture-advanced-joinery/`.

## After import

Leave posts in Draft. Publication is a later verb.
