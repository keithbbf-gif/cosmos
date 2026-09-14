# MERGE_REPORT — furniture-craft-blog pack

**Date:** 2026-09-14  
**Unified branch:** `cursor/furniture-craft-unified-c264`  
**Inputs:**

| PR | Branch | Role |
|----|--------|------|
| [#263](https://github.com/keithbbf-gif/cosmos/pull/263) | `cursor/furniture-craft-merge-1ad4` | Prose + **45 SVG assets**, `GRAPHIC_MAP.yaml`, embedded `<figure class="craft-figure">`, `GRAPHICS_INDEX.md`, merge tooling |
| [#272](https://github.com/keithbbf-gif/cosmos/pull/272) | `cursor/furniture-craft-editor-dde6` | Grammar/voice QA on all 44 essays, dedupe, `voice_check: edited`, `EDITOR_REPORT.md`, refreshed `MANIFEST.md` |

**Prose lineage:** `cursor/furniture-craft-blog-623a` (PR #251 magazine pack).

## Outcome

Single tree at `content/furniture-craft-blog/`:

| Lane | Kept | Notes |
|------|------|-------|
| Prose | 44 magazine drafts | **Editor body copy** (#272); not reverted to pre-editor or graphics-stub text |
| Voice | `voice_check: edited` on all 44 | Photo `figures:` YAML + `[VERIFY]` lines preserved |
| Diagrams | 45 SVGs + inline embeds | One or two `<figure class="craft-figure">` per essay; `graphics:` front matter |
| Photos | `figures:` BBF paths, `PHOTO_CAPTIONS.md` | Still `status: needed` until shop pull — unchanged by this merge |
| Docs | `STYLE_GUIDE.md` (magazine + Figures section), `EDITOR_REPORT.md`, `GRAPHICS_MERGE_NOTE.md`, `BIBLIOGRAPHY.md`, `WP_IMPORT.md`, `INDEX.md`, `MANIFEST.md` | `MERGE_REPORT.md` (this file) |

**Tooling:** `tools/merge_furniture_craft_editor_stack.py` — takes editor drafts from `origin/cursor/furniture-craft-editor-dde6`, re-applies SVG blocks from `GRAPHIC_MAP.yaml` + graphics-pack captions. Safe to re-run after prose edits.

## Conflicts resolved (#263 vs #272)

1. **Prose vs figures** — #272 removed SVG embeds (editor scope was YAML photos only). Unified tree restores embeds without touching editor sentences.
2. **`voice_check`** — Unified pack uses `edited` (#272), not `human` (#263).
3. **`word_count`** — Editor recounts retained; bodies match #272 except for figure HTML (not counted in `word_count`).
4. **Duplicate `graphics:` keys** — #263 had occasional duplicated YAML keys; `update_front_matter()` emits one `graphics:` block per draft.
5. **Asset tree** — #272 branch omitted `assets/`; unified tree keeps full #263 SVG inventory.

## Verification (unified pass)

```bash
# 44 essays, editor voice flag
grep -l 'voice_check: edited' content/furniture-craft-blog/drafts/*.md | wc -l

# 44 essays with embedded SVG figures
grep -l 'craft-figure' content/furniture-craft-blog/drafts/*.md | wc -l

# 45 SVG files on disk
find content/furniture-craft-blog/assets -name '*.svg' | wc -l

# GRAPHIC_MAP covers GRAPHICS_INDEX slugs
python3 -c "import yaml,re; from pathlib import Path; m=yaml.safe_load(Path('content/furniture-craft-blog/GRAPHIC_MAP.yaml').read_text()); used=set(s for v in m.values() for s in v); all=set(re.findall(r'\| \d+ \| \`([^\`]+)\`', Path('content/furniture-craft-blog/GRAPHICS_INDEX.md').read_text())); assert not (all-used)"
```

Expected: `44`, `44`, `45`, no assertion error.

## Re-run workflow

1. Edit prose in `drafts/`; keep `voice_check: edited` when grammar QA still applies.
2. `python3 tools/merge_furniture_craft_editor_stack.py` — refreshes SVG HTML + `graphics:` YAML from map.
3. If SVG art changes: `python3 tools/generate_furniture_craft_blog_graphics.py`, then step 2.
4. Shop photo pulls: update `figures:` + `PHOTO_CAPTIONS.md` only; do not remove diagram embeds.

## PR stack

- **Review target:** merge `cursor/furniture-craft-unified-c264` into `cursor/furniture-craft-merge-1ad4`, then stack to #251 / `main` when approved.
- #272 can close after unified merge lands; #263 remains the graphics parent until unified is merged.
