# Graphics merge note — Furniture Craft Blog Pack

**For:** merge agents on [#235](https://github.com/keithbbf-gif/cosmos/issues/235) / [#241](https://github.com/keithbbf-gif/cosmos/issues/241) and stacked PR on `cursor/furniture-craft-blog-623a`.

**Editor pass (2026-09-14):** No inline Markdown image embeds were added or removed in essay bodies. All figure metadata remains in YAML front matter (`figures:` blocks) and in `PHOTO_CAPTIONS.md`.

## Current state

- **44 / 44** drafts list at least one figure with `status: needed`.
- Preferred paths point at `D:\BBF\BBF Photos` (or LOC Sanborn on essay 27) with **filename pending shop pull** — see `PHOTO_CAPTIONS.md`.
- No essay body contains `![` image syntax today; WordPress attachment happens after files exist (`WP_IMPORT.md`).

## What the merge agent should do

1. Match each `fig-*` id to a real file from Keith’s library (or approved historical asset); copy **actual filename** and any metadata credit into front matter.
2. Set `status:` to `ready` (or equivalent) only when owner clearance and license lines are filled — do not invent credits.
3. Historical / LOC items: confirm item URL and rights line before public embed (`[VERIFY rights]` where noted).
4. If a figure is intentionally deferred, leave front matter as `needed` and note the slug here.

## Slugs with external / rights-sensitive figures

| slug | figure id | note |
|---|---|---|
| `from-the-yard-to-the-room` | fig-02 | LOC Sanborn Warren 1907 — confirm item URL + rights before embed |

All other shop figures are **needed pulls** from `D:\BBF\BBF Photos` per caption in `PHOTO_CAPTIONS.md`.

## Editor preservation

Do not strip `figures:` YAML when merging graphics. If you add body embeds for WordPress preview, keep front matter as the authority for captions, credit, and license.
