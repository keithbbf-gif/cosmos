# Merge report — ancient furniture history blog pack

**Date:** 2026-09-14  
**Target tree:** `content/furniture-history-ancient-blog/`  
**Unified branch:** `cursor/furniture-ancient-unified-bcfa`

## Source pull requests

| PR | Branch | Role in merge |
| --- | --- | --- |
| [#253](https://github.com/keithbbf-gif/cosmos/pull/253) | `cursor/furniture-history-ancient-blog-bbf1` | **Canonical prose:** forty-three magazine essays (1,800–2,800 body words), `INDEX.md`, `BIBLIOGRAPHY.md`, `PHOTO_CAPTIONS.md`, `TIMELINE.md`, `STYLE_GUIDE.md` |
| [#236](https://github.com/keithbbf-gif/cosmos/pull/236) | `cursor/furniture-ancient-graphics-2a96` | **Figures:** 44 topic slugs × four SVG schematics (`timeline`, `map`, `typology`, `plate`), `GRAPHICS_INDEX.md`, `LICENSES.md`, `topics.json`, `scripts/build_graphics_pack.py` |
| [#248](https://github.com/keithbbf-gif/cosmos/pull/248) | `cursor/citation-deepen-ancient-furniture-8a9f` | **Citation pass:** seven strengthened draft essays + `CITATION_PASS_REPORT.md` (evidence paragraphs ported into matching magazine chapters; see below) |

## Merge decisions

1. **One essay series, not two.** The forty-four `drafts/*.md` files from the graphics/citation lineage are **not** duplicated in this tree. Magazine chapters `01`–`43` remain authoritative for voice and length. Graphics slugs attach through `CHAPTER_GRAPHICS_MAP.json`.
2. **Four schematics per chapter.** Each chapter’s `## Figure plan` now leads with Figs. 1–4 (embedded SVG paths under `assets/<slug>/`). Former photo/redraw entries are preserved under `### Supplemental photographs and redraws`, renumbered from Fig. 5 upward.
3. **Thematic mapping for later chapters.** Slugs 26–43 reuse cross-cutting asset sets (`joinery-before-nails`, `pigment-and-gilding-furniture`, `reconstruction-methods-museums`, etc.) where no period-specific ancient pack exists. Mapping rationale is explicit in `CHAPTER_GRAPHICS_MAP.json` (no hidden one-to-one claim).
4. **Citation port (prose).** Paragraphs from the PR #248 citation pass were merged into magazine chapters where topics align:
   - `02-platforms-catalhoyuk` — Indus platform evidence (Marshall, Kenoyer)
   - `12-late-antique-byzantine` — catacomb loculi / arcosolia (ICS grammar)
   - `16-kutubiyya-minbar` — Bloom & Hbibi 1998 on **ʿAzīz** inscription
   - `18-china-before-ming` — kang antecedents, Dongheishan
   - `21-joseon-korea` — Goguryeo fort ondol (Mt. Acha Fort 4)
   - `22-south-asia-seats` — Mauryan textual/architectural evidence (Strabo, Kumrahar, *Arthashastra*)
5. **Remaining `[CITE NEEDED]` markers** in later and regional chapters are intentional editor flags (see `STYLE_GUIDE.md`). Count after merge: run `rg -c 'CITE NEEDED' content/furniture-history-ancient-blog/[0-9]*.md`.

## Inventory after merge

| Item | Count |
| --- | ---: |
| Magazine essays | 43 |
| SVG files under `assets/` | 348 (44 topic slugs × 4 + 43 chapter slugs × 4) |
| Chapters with embedded Figs. 1–4 | 43 (chapter-specific paths, wave 2) |
| Scripts | `scripts/merge_unified_figures.py`, `scripts/build_graphics_pack.py`, `scripts/build_chapter_graphics_wave2.py`, `scripts/refresh_chapter_figure_embeds.py`, … |

## Wave 2 — chapter-specific schematics (2026-09-14)

**Problem:** After the unified merge, twenty-four magazine chapters still borrowed cross-cutting ancient topic slugs (`pigment-and-gilding-furniture`, `joinery-before-nails`, etc.). Timelines read “2000 BCE–500 CE” on Renaissance and modern chapters.

**Fix:** One schematic set per chapter stem under `assets/<chapter-stem>/`, with metadata in `chapter_graphics_meta.json` (period, region, typology labels). `CHAPTER_GRAPHICS_MAP.json` is now 1:1 (chapter → same stem). The original forty-four ancient topic packs under `assets/<topics.json slug>/` remain for the editorial deep-dive lineage.

**Regenerate chapter figures:**

```bash
python3 content/furniture-history-ancient-blog/scripts/build_chapter_graphics_wave2.py
python3 content/furniture-history-ancient-blog/scripts/refresh_chapter_figure_embeds.py
```

## Regeneration

To re-apply schematic embeds after editing `CHAPTER_GRAPHICS_MAP.json`:

```bash
python3 content/furniture-history-ancient-blog/scripts/merge_unified_figures.py
```

The script skips essays that already contain `assets/<slug>/fig-01-timeline.svg`.

## Not merged / deferred

- Duplicate `drafts/` tree from PRs #236/#248 (superseded by magazine chapters + this report).
- `EDITOR_REPORT.md` from the graphics editor pass (weak-article flags addressed in citation branch drafts only).
- Automated resolution of all seventy-eight `[CITE NEEDED]` instances in the magazine series — requires museum accession confirmation and local-history archives (e.g. Fort Smith directories).

## QA checklist for human editor

- [ ] Spot-read Figs. 1–4 captions against each chapter’s period (thematic reuse in ch. 26–43).
- [ ] Confirm `PHOTO_CAPTIONS.md` still matches supplemental figure numbers (now Fig. 5+).
- [ ] Word-count band in `MANIFEST.md` after prose inserts (re-run count script if present).
- [ ] WordPress import (`WP_IMPORT.md`) with relative `assets/` paths.
