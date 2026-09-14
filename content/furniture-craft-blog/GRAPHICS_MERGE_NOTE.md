# Graphics merge note — Furniture Craft Blog Pack

**Unified stack (2026-09-14):** PR [#263](https://github.com/keithbbf-gif/cosmos/pull/263) (`cursor/furniture-craft-merge-1ad4`) + PR [#272](https://github.com/keithbbf-gif/cosmos/pull/272) (`cursor/furniture-craft-editor-dde6`) → `cursor/furniture-craft-unified-c264`.

## Current state

- **44 / 44** drafts carry `voice_check: edited` body copy from the editor pass.
- **44 / 44** drafts embed at least one cream/ink **SVG** via `<figure class="craft-figure">` (see `graphics:` in front matter and `GRAPHICS_INDEX.md`).
- **45** SVG files under `assets/`; mapping in `GRAPHIC_MAP.yaml`.
- **Shop photos** remain in YAML `figures:` only (`status: needed` until `D:\BBF\BBF Photos` pulls land). Captions: `PHOTO_CAPTIONS.md`. No `![` Markdown photo syntax in bodies.

## Photo merge (still open)

1. Match each `fig-*` id to a real file from Keith’s library (or approved historical asset); copy **actual filename** and metadata credit into front matter.
2. Set `status:` to `ready` only when owner clearance and license lines are filled — do not invent credits.
3. Historical / LOC items: confirm item URL and rights line before public embed (`[VERIFY rights]` where noted).

## Slugs with external / rights-sensitive figures

| slug | figure id | note |
|---|---|---|
| `from-the-yard-to-the-room` | fig-02 | LOC Sanborn Warren 1907 — confirm item URL + rights before embed |

## Preservation rules

- Do not strip `figures:` YAML when editing prose or SVGs.
- Do not replace editor body copy with graphics-stub drafts from the old topic-keyed pack.
- After prose edits, re-run `python3 tools/merge_furniture_craft_editor_stack.py` so SVG embeds stay aligned with `GRAPHIC_MAP.yaml`.
